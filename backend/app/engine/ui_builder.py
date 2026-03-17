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
    Returns a dictionary that can be used to instantiate the model.
    """
    data = {}
    initial_data = initial_data or {}
    
    # Get the fields of the model
    fields = model_class.model_fields
    
    for field_name, field_info in fields.items():
        label = field_info.alias or field_name
        field_type = field_info.annotation
        
        # Determine default value: 
        # 1. from initial_data (loaded project)
        # 2. from model default
        if field_name in initial_data:
            default_value = initial_data[field_name]
        elif field_info.default is not PydanticUndefined:
            default_value = field_info.default
        else:
            default_value = None
            
        # Determine the key for the widget to avoid collisions
        widget_key = f"{key_prefix}_{field_name}"
        
        # Handle Union (e.g., Union[float, RotateSettings])
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
                
                # If we have initial data, try to guess the type
                default_type_idx = 0
                if isinstance(default_value, dict) and "type" in default_value:
                    # Very specific to J2V, but often unions are discriminated by 'type'
                    pass # complicated to match perfectly here without more logic
                
                selected_type_label = st.selectbox(f"Type for {label}", type_labels, index=default_type_idx, key=f"{widget_key}_type")
                selected_type = non_none_args[type_labels.index(selected_type_label)]
                
                if isinstance(selected_type, type) and issubclass(selected_type, BaseModel):
                    with st.expander(f"{label} ({selected_type_label})"):
                        data[field_name] = pydantic_form(selected_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
                    continue
                else:
                    field_type = selected_type
                    origin = get_origin(field_type)
                    args = get_args(field_type)

        # Handle Literal (selectbox)
        if origin is Literal:
            idx = 0
            if default_value in args:
                idx = args.index(default_value)
            data[field_name] = st.selectbox(label, args, index=idx, key=widget_key)
        
        # Handle Basic Types
        elif field_type is str:
            data[field_name] = st.text_input(label, value=str(default_value) if default_value is not None else "", key=widget_key)
        elif field_type is int:
            data[field_name] = st.number_input(label, value=int(default_value) if default_value is not None else 0, step=1, key=widget_key)
        elif field_type is float:
            data[field_name] = st.number_input(label, value=float(default_value) if default_value is not None else 0.0, step=0.1, key=widget_key)
        elif field_type is bool:
            data[field_name] = st.checkbox(label, value=bool(default_value) if default_value is not None else False, key=widget_key)
        
        # Handle Nested BaseModel
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            with st.expander(label):
                data[field_name] = pydantic_form(field_type, key_prefix=f"{widget_key}_nested", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None)
        
        # Handle List
        elif origin is list:
            item_type = args[0]
            st.write(f"### {label} (List)")
            
            list_key = f"{widget_key}_list_count"
            if list_key not in st.session_state:
                st.session_state[list_key] = len(default_value) if isinstance(default_value, list) else 0
            
            col1, col2 = st.columns(2)
            if col1.button(f"Add Item to {label}", key=f"{widget_key}_add"):
                st.session_state[list_key] += 1
            if col2.button(f"Remove Item from {label}", key=f"{widget_key}_remove") and st.session_state[list_key] > 0:
                st.session_state[list_key] -= 1
            
            items = []
            for i in range(st.session_state[list_key]):
                st.markdown(f"---")
                st.markdown(f"**{label} - Item {i+1}**")
                
                item_initial = default_value[i] if isinstance(default_value, list) and i < len(default_value) else None
                
                # Special case for polymorphic elements using registry
                if registry and (item_type is dict or item_type is Any):
                    default_reg_idx = 0
                    if isinstance(item_initial, dict) and "type" in item_initial:
                        if item_initial["type"] in registry:
                            default_reg_idx = list(registry.keys()).index(item_initial["type"])
                            
                    selected_type_key = st.selectbox(f"Select Type for {label} [{i}]", list(registry.keys()), index=default_reg_idx, key=f"{widget_key}_{i}_type")
                    selected_model = registry[selected_type_key]
                    items.append(pydantic_form(selected_model, key_prefix=f"{widget_key}_{i}", registry=registry, initial_data=item_initial if isinstance(item_initial, dict) else None))
                
                elif isinstance(item_type, type) and issubclass(item_type, BaseModel):
                    items.append(pydantic_form(item_type, key_prefix=f"{widget_key}_{i}", registry=registry, initial_data=item_initial if isinstance(item_initial, dict) else None))
                else:
                    items.append(st.text_input(f"{label} [{i}]", value=str(item_initial) if item_initial is not None else "", key=f"{widget_key}_{i}"))
            data[field_name] = items
            
        # Fallback for Dict
        elif field_type is dict or origin is dict:
            val = st.text_area(label + " (JSON)", value="{}" if default_value is None else json.dumps(default_value), key=widget_key)
            try:
                data[field_name] = json.loads(val)
            except:
                data[field_name] = {}
        else:
            if hasattr(field_type, "__name__"):
                 st.info(f"Field {field_name} has complex/unsupported type {field_type}. Using JSON input.")
                 val = st.text_area(label + " (JSON)", value="{}" if default_value is None else json.dumps(default_value), key=widget_key)
                 try:
                     data[field_name] = json.loads(val)
                 except:
                     data[field_name] = {}
            
    return data
