import streamlit as st
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from typing import Any, Dict, List, Type, Union, get_args, get_origin, Literal, Optional, Annotated
import json

def pydantic_form(
    model_class: Type[BaseModel], 
    key_prefix: str = "", 
    registry: Optional[Dict[str, Type[BaseModel]]] = None,
    initial_data: Optional[Dict[str, Any]] = None,
    exclude_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Dynamically generates Streamlit widgets for ALL fields in a Pydantic model.
    """
    data = {}
    initial_data = initial_data or {}
    exclude_fields = exclude_fields or []
    
    fields = model_class.model_fields
    
    for field_name, field_info in fields.items():
        if field_name in exclude_fields:
            continue
            
        label = field_info.alias or field_name
        field_type = field_info.annotation
        help_text = field_info.description or ""
        
        # Determine value (priority: initial_data > model default > None)
        if field_name in initial_data:
            default_value = initial_data[field_name]
        elif field_info.default is not PydanticUndefined:
            default_value = field_info.default
        else:
            default_value = None
            
        widget_key = f"{key_prefix}_{field_name}"
        
        # Handle Union/Annotated types (Discriminated Unions)
        origin = get_origin(field_type)
        args = get_args(field_type)
        
        # Unpack Annotated if needed
        if origin is Annotated:
            field_type = args[0]
            origin = get_origin(field_type)
            args = get_args(field_type)

        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                field_type = non_none_args[0]
                origin = get_origin(field_type)
                args = get_args(field_type)
            else:
                # Polimorphic Union (e.g. List[J2VAnyElement])
                # We handle this by letting the user choose the type if not already set
                type_labels = [str(arg.__name__ if hasattr(arg, "__name__") else arg) for arg in non_none_args]
                
                # Try to detect type from initial data
                default_type_idx = 0
                if isinstance(default_value, dict) and "type" in default_value:
                    t = default_value["type"].lower()
                    for idx, arg in enumerate(non_none_args):
                        if hasattr(arg, "model_fields") and "type" in arg.model_fields:
                            f = arg.model_fields["type"]
                            if hasattr(f, "default") and str(f.default).lower() == t:
                                default_type_idx = idx
                                break

                selected_label = st.selectbox(f"Select Type for {label}", type_labels, index=default_type_idx, key=f"{widget_key}_union_type")
                selected_type = non_none_args[type_labels.index(selected_label)]
                
                if isinstance(selected_type, type) and issubclass(selected_type, BaseModel):
                    data[field_name] = pydantic_form(selected_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
                    continue
                else:
                    field_type = selected_type
                    origin = get_origin(field_type)
                    args = get_args(field_type)

        # 1. Handle Literal (Selectbox)
        if origin is Literal:
            options = args
            idx = options.index(default_value) if default_value in options else 0
            data[field_name] = st.selectbox(label, options, index=idx, key=widget_key, help=help_text)
        
        # 2. Basic Types
        elif field_type is str:
            data[field_name] = st.text_input(label, value=str(default_value) if default_value is not None else "", key=widget_key, help=help_text)
        elif field_type is int:
            data[field_name] = st.number_input(label, value=int(default_value) if default_value is not None else 0, step=1, key=widget_key, help=help_text)
        elif field_type is float:
            # Handle float fields, ensure step is float
            val = float(default_value) if default_value is not None else 0.0
            data[field_name] = st.number_input(label, value=val, step=0.1, key=widget_key, help=help_text)
        elif field_type is bool:
            data[field_name] = st.checkbox(label, value=bool(default_value), key=widget_key, help=help_text)
        
        # 3. Nested Models
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            with st.expander(f"⚙️ {label}"):
                data[field_name] = pydantic_form(field_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
        
        # 4. Dict / Variables (Key-Value Editor)
        elif field_type is dict or origin is dict:
            st.write(f"🔗 **{label}**")
            kv_key = f"{widget_key}_kv_state"
            if kv_key not in st.session_state:
                st.session_state[kv_key] = list(default_value.items()) if isinstance(default_value, dict) else []
            
            if st.button(f"➕ Add to {label}", key=f"{widget_key}_add_kv"):
                st.session_state[kv_key].append(("", ""))
                st.rerun()
            
            updated_dict = {}
            for i, (k, v) in enumerate(st.session_state[kv_key]):
                c1, c2, c3 = st.columns([2, 2, 1])
                nk = c1.text_input("Key", value=k, key=f"{widget_key}_k_{i}", label_visibility="collapsed")
                nv = c2.text_input("Value", value=str(v), key=f"{widget_key}_v_{i}", label_visibility="collapsed")
                if c3.button("🗑️", key=f"{widget_key}_del_{i}"):
                    st.session_state[kv_key].pop(i)
                    st.rerun()
                if nk: updated_dict[nk] = nv
            data[field_name] = updated_dict

        # 5. List (Recursive but controlled by streamlit_app for J2VMovie)
        elif origin is list:
            # We only use this for simple lists. 
            # For J2VMovie.scenes and J2VScene.elements we handle it in streamlit_app.py for better UX
            st.write(f"📋 {label}")
            item_type = args[0]
            items = []
            count_key = f"{widget_key}_l_count"
            if count_key not in st.session_state:
                st.session_state[count_key] = len(default_value) if isinstance(default_value, list) else 0
            
            for i in range(st.session_state[count_key]):
                val = default_value[i] if isinstance(default_value, list) and i < len(default_value) else {}
                items.append(pydantic_form(item_type, key_prefix=f"{widget_key}_{i}", initial_data=val))
            data[field_name] = items
            
    return data
