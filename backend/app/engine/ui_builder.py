import streamlit as st
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from typing import Any, Dict, List, Type, Union, get_args, get_origin, Literal, Optional
import json

def pydantic_form(
    model_class: Type[BaseModel], 
    key_prefix: str = "", 
    registry: Optional[Dict[str, Type[BaseModel]]] = None,
    initial_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dynamically generates Streamlit widgets based on a Pydantic model.
    """
    data = {}
    initial_data = initial_data or {}
    
    fields = model_class.model_fields
    
    for field_name, field_info in fields.items():
        label = field_info.alias or field_name
        field_type = field_info.annotation
        help_text = field_info.description or ""
        
        if field_name in initial_data:
            default_value = initial_data[field_name]
        elif field_info.default is not PydanticUndefined:
            default_value = field_info.default
        else:
            default_value = None
            
        widget_key = f"{key_prefix}_{field_name}"
        
        # Handle Union
        origin = get_origin(field_type)
        args = get_args(field_type)
        
        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                field_type = non_none_args[0]
                origin = get_origin(field_type)
                args = get_args(field_type)
            else:
                type_labels = [str(arg.__name__ if hasattr(arg, "__name__") else arg) for arg in non_none_args]
                
                # Auto-select type based on 'type' field in initial data
                default_idx = 0
                if isinstance(default_value, dict) and "type" in default_value:
                    target_type_name = default_value["type"].lower()
                    for i, arg in enumerate(non_none_args):
                        if hasattr(arg, "model_fields") and "type" in arg.model_fields:
                            # This is a bit hacky, but check Literal default
                            type_field = arg.model_fields["type"]
                            if hasattr(type_field, "default") and str(type_field.default).lower() == target_type_name:
                                default_idx = i
                                break

                selected_type_label = st.selectbox(f"Type for {label}", type_labels, index=default_idx, key=f"{widget_key}_type", help=help_text)
                selected_type = non_none_args[type_labels.index(selected_type_label)]
                
                if isinstance(selected_type, type) and issubclass(selected_type, BaseModel):
                    with st.container(border=True):
                        st.caption(f"Settings for {selected_type_label}")
                        data[field_name] = pydantic_form(selected_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
                    continue
                else:
                    field_type = selected_type
                    origin = get_origin(field_type)
                    args = get_args(field_type)

        # Handle Literal
        if origin is Literal:
            idx = 0
            if default_value in args:
                idx = args.index(default_value)
            data[field_name] = st.selectbox(label, args, index=idx, key=widget_key, help=help_text)
        
        # Handle Basic Types
        elif field_type is str:
            data[field_name] = st.text_input(label, value=str(default_value) if default_value is not None else "", key=widget_key, help=help_text)
        elif field_type is int:
            data[field_name] = st.number_input(label, value=int(default_value) if default_value is not None else 0, step=1, key=widget_key, help=help_text)
        elif field_type is float:
            data[field_name] = st.number_input(label, value=float(default_value) if default_value is not None else 0.0, step=0.1, key=widget_key, help=help_text)
        elif field_type is bool:
            data[field_name] = st.checkbox(label, value=bool(default_value) if default_value is not None else False, key=widget_key, help=help_text)
        
        # Handle Nested BaseModel
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            with st.expander(label):
                data[field_name] = pydantic_form(field_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
        
        # Handle List
        elif origin is list:
            item_type = args[0]
            st.write(f"**{label}**")
            
            list_key = f"{widget_key}_list_count"
            if list_key not in st.session_state:
                st.session_state[list_key] = len(default_value) if isinstance(default_value, list) else 0
            
            col1, col2 = st.columns(2)
            if col1.button(f"➕ Add to {label}", key=f"{widget_key}_add"):
                st.session_state[list_key] += 1
                st.rerun()
            if col2.button(f"➖ Remove from {label}", key=f"{widget_key}_remove") and st.session_state[list_key] > 0:
                st.session_state[list_key] -= 1
                st.rerun()
            
            items = []
            for i in range(st.session_state[list_key]):
                item_initial = default_value[i] if isinstance(default_value, list) and i < len(default_value) else {}
                
                with st.container(border=True):
                    st.caption(f"{label} Item #{i+1}")
                    # Special case for polymorphic elements using registry
                    if registry and (item_type is dict or item_type is Any or get_origin(item_type) is Union):
                        default_reg_idx = 0
                        if isinstance(item_initial, dict) and "type" in item_initial:
                            if item_initial["type"] in registry:
                                default_reg_idx = list(registry.keys()).index(item_initial["type"])
                                
                        selected_type_key = st.selectbox(f"Select Type", list(registry.keys()), index=default_reg_idx, key=f"{widget_key}_{i}_type")
                        selected_model = registry[selected_type_key]
                        items.append(pydantic_form(selected_model, key_prefix=f"{widget_key}_{i}", registry=registry, initial_data=item_initial if isinstance(item_initial, dict) else None))
                    elif isinstance(item_type, type) and issubclass(item_type, BaseModel):
                        items.append(pydantic_form(item_type, key_prefix=f"{widget_key}_{i}", registry=registry, initial_data=item_initial if isinstance(item_initial, dict) else None))
                    else:
                        items.append(st.text_input(f"Item #{i+1}", value=str(item_initial) if item_initial else "", key=f"{widget_key}_{i}"))
            data[field_name] = items
            
        # Handle Dict (Improved Key-Value Editor)
        elif field_type is dict or origin is dict:
            st.write(f"**{label} (Key-Value Pairs)**")
            
            kv_key = f"{widget_key}_kv_count"
            current_dict = default_value if isinstance(default_value, dict) else {}
            
            if kv_key not in st.session_state:
                st.session_state[kv_key] = list(current_dict.items())
            
            # Helper to add a new pair
            if st.button(f"➕ Add Entry to {label}", key=f"{widget_key}_kv_add"):
                st.session_state[kv_key].append(("", ""))
                st.rerun()
            
            updated_dict = {}
            to_remove = None
            
            for i, (k, v) in enumerate(st.session_state[kv_key]):
                c1, c2, c3 = st.columns([2, 2, 1])
                new_k = c1.text_input(f"Key {i}", value=k, key=f"{widget_key}_k_{i}")
                # Value can be string or nested JSON
                val_str = v if isinstance(v, (str, int, float, bool)) else json.dumps(v)
                new_v_raw = c2.text_input(f"Value {i}", value=str(val_str), key=f"{widget_key}_v_{i}")
                
                # Try to parse as JSON if it looks like it, otherwise keep as string
                try:
                    new_v = json.loads(new_v_raw) if (new_v_raw.startswith("{") or new_v_raw.startswith("[")) else new_v_raw
                except:
                    new_v = new_v_raw
                
                if c3.button("🗑️", key=f"{widget_key}_del_{i}"):
                    to_remove = i
                
                if new_k:
                    updated_dict[new_k] = new_v
            
            if to_remove is not None:
                st.session_state[kv_key].pop(to_remove)
                st.rerun()
                
            data[field_name] = updated_dict
            
        else:
            if hasattr(field_type, "__name__"):
                 st.info(f"Field {field_name} has complex type {field_type}. Using JSON area.")
                 val = st.text_area(label + " (JSON)", value="{}" if default_value is None else json.dumps(default_value), key=widget_key)
                 try:
                     data[field_name] = json.loads(val)
                 except:
                     data[field_name] = {}
            
    return data
