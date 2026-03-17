import streamlit as st
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from typing import Any, Dict, List, Type, Union, get_args, get_origin, Literal, Optional, Annotated
import json
import os
import uuid
from .asset_manager import AssetManager

# Define which fields should be at the top for each model
PRIORITY_FIELDS = {
    "J2VMovie": ["width", "height", "fps", "resolution"],
    "J2VScene": ["duration", "background_color", "iterate"], # Removed 'id' to hide it
    "ImageElement": ["src", "width", "height", "resize", "position"],
    "TextElement": ["text", "style", "width", "height", "position"],
    "AudioElement": ["src", "volume", "loop", "seek"],
    "VideoElement": ["src", "width", "height", "volume", "loop"],
    "VoiceElement": ["text", "voice", "model", "volume"],
    "AudiogramElement": ["color", "amplitude", "opacity"],
    "SubtitlesElement": ["captions", "language", "model"],
    "ComponentElement": ["component", "width", "height"],
    "SubtitlesSettings": ["style", "font_family", "font_size", "font_color"]
}

def render_field_row(label: str, help_text: str, widget_func, *args, **kwargs):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<div style='padding-top: 10px; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        kwargs["label_visibility"] = "collapsed"
        kwargs["label"] = label
        return widget_func(*args, **kwargs)

def pydantic_form(
    model_class: Type[BaseModel], 
    key_prefix: str = "", 
    registry: Optional[Dict[str, Type[BaseModel]]] = None,
    initial_data: Optional[Dict[str, Any]] = None,
    exclude_fields: List[str] = None,
    asset_mgr: Optional[AssetManager] = None
) -> Dict[str, Any]:
    data = {}
    initial_data = initial_data or {}
    exclude_fields = exclude_fields or []
    
    fields = model_class.model_fields
    model_name = model_class.__name__
    
    priority_keys = PRIORITY_FIELDS.get(model_name, [])
    all_keys = [k for k in fields.keys() if k not in exclude_fields]
    top_keys = [k for k in all_keys if k in priority_keys]
    other_keys = [k for k in all_keys if k not in priority_keys]

    def render_logic(keys_list):
        for field_name in keys_list:
            field_info = fields[field_name]
            label = field_info.alias or field_name
            field_type = field_info.annotation
            help_text = field_info.description or ""
            
            # --- AUTO ID GEN ---
            if field_name == "id" and field_name not in initial_data:
                data[field_name] = f"{model_name.lower().replace('element', '')}_{uuid.uuid4().hex[:6]}"
                continue
            
            if field_name in initial_data: default_value = initial_data[field_name]
            elif field_info.default is not PydanticUndefined: default_value = field_info.default
            else: default_value = None
            
            widget_key = f"{key_prefix}_{field_name}"
            
            # 1. SPECIAL: Asset Picker
            if field_name == "src" and asset_mgr:
                asset_type = "image"
                if "Audio" in model_name: asset_type = "audio"
                elif "Video" in model_name: asset_type = "video"
                with st.container(border=True):
                    st.caption(f"📁 {label.upper()} ({asset_type})")
                    current_val = str(default_value or "")
                    if current_val:
                        try:
                            full_path = current_val if current_val.startswith("/data/") else os.path.join(os.getenv("ASSET_PATH", "/data/assets"), current_val.lstrip("/"))
                            if os.path.exists(full_path):
                                if asset_type == "image": st.image(full_path, width=150)
                                elif asset_type == "video": st.video(full_path)
                                elif asset_type == "audio": st.audio(full_path)
                        except: pass
                    m_col1, m_col2 = st.columns([1, 2])
                    mode = m_col1.radio("Mode", ["Lib", "Up", "URL"], key=f"{widget_key}_mode", label_visibility="collapsed")
                    if mode == "Lib":
                        assets = asset_mgr.list_assets(asset_type)
                        opts = {a["name"]: a["rel_path"] for a in assets}
                        curr_idx = (list(opts.values()).index(current_val) + 1) if current_val in opts.values() else 0
                        sel = m_col2.selectbox("Lib", ["-- Select --"] + list(opts.keys()), index=curr_idx, key=f"{widget_key}_lib", label_visibility="collapsed")
                        data[field_name] = opts[sel] if sel != "-- Select --" else current_val
                    elif mode == "Up":
                        up = m_col2.file_uploader("Up", key=f"{widget_key}_up", label_visibility="collapsed")
                        if up: data[field_name] = asset_mgr.upload_asset(asset_type, up.name, up.read())
                        else: data[field_name] = current_val
                    else: data[field_name] = m_col2.text_input("URL", value=current_val, key=f"{widget_key}_url", label_visibility="collapsed")
                continue

            # 2. Polymorphic
            origin = get_origin(field_type)
            args = get_args(field_type)
            if origin is Annotated: field_type = args[0]; origin = get_origin(field_type); args = get_args(field_type)

            if origin is Union:
                non_none = [arg for arg in args if arg is not type(None)]
                if len(non_none) == 1:
                    field_type = non_none[0]; origin = get_origin(field_type); args = get_args(field_type)
                else:
                    labels = [str(arg.__name__ if hasattr(arg, "__name__") else arg) for arg in non_none]
                    d_idx = 0
                    if isinstance(default_value, dict) and "type" in default_value:
                        t = default_value["type"].lower()
                        for idx, arg in enumerate(non_none):
                            if hasattr(arg, "model_fields") and "type" in arg.model_fields:
                                f = arg.model_fields["type"]
                                if hasattr(f, "default") and str(f.default).lower() == t:
                                    d_idx = idx; break
                    sel_label = render_field_row(label, help_text, st.selectbox, options=labels, index=d_idx, key=f"{widget_key}_u_type", help=help_text)
                    sel_type = non_none[labels.index(sel_label)]
                    if isinstance(sel_type, type) and issubclass(sel_type, BaseModel):
                        data[field_name] = pydantic_form(sel_type, key_prefix=f"{widget_key}_n", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None, asset_mgr=asset_mgr)
                        continue
                    else: field_type = sel_type; origin = get_origin(field_type); args = get_args(field_type)

            # 3. Widgets
            if origin is Literal:
                options = args
                idx = options.index(default_value) if default_value in options else 0
                data[field_name] = render_field_row(label, help_text, st.selectbox, options=options, index=idx, key=widget_key, help=help_text)
            elif field_type is str:
                data[field_name] = render_field_row(label, help_text, st.text_input, value=str(default_value or ""), key=widget_key, help=help_text)
            elif field_type is int:
                data[field_name] = render_field_row(label, help_text, st.number_input, value=int(default_value or 0), step=1, key=widget_key, help=help_text)
            elif field_type is float:
                data[field_name] = render_field_row(label, help_text, st.number_input, value=float(default_value or 0.0), step=0.1, key=widget_key, help=help_text)
            elif field_type is bool:
                data[field_name] = render_field_row(label, help_text, st.checkbox, value=bool(default_value), key=widget_key, help=help_text)
            elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                with st.expander(f"⚙️ {label}"):
                    data[field_name] = pydantic_form(field_type, key_prefix=f"{widget_key}_n", registry=registry, initial_data=default_value if isinstance(default_value, dict) else None, asset_mgr=asset_mgr)
            elif field_type is dict or origin is dict:
                st.markdown(f"**{label}**")
                kv_key = f"{widget_key}_kv"
                if kv_key not in st.session_state: st.session_state[kv_key] = list(default_value.items()) if isinstance(default_value, dict) else []
                if st.button(f"➕ Add to {label}", key=f"{widget_key}_add_kv"): st.session_state[kv_key].append(("", "")); st.rerun()
                upd = {}
                for idx, (k, v) in enumerate(st.session_state[kv_key]):
                    r1, r2, r3 = st.columns([2, 2, 1])
                    nk = r1.text_input("K", value=k, key=f"{widget_key}_k_{idx}", label_visibility="collapsed")
                    nv = r2.text_input("V", value=str(v), key=f"{widget_key}_v_{idx}", label_visibility="collapsed")
                    if r3.button("🗑️", key=f"{widget_key}_d_{idx}"): st.session_state[kv_key].pop(idx); st.rerun()
                    if nk: upd[nk] = nv
                data[field_name] = upd
            elif origin is list:
                st.write(f"📋 {label}")
                it = args[0]
                ck = f"{widget_key}_list"
                if ck not in st.session_state: st.session_state[ck] = len(default_value) if isinstance(default_value, list) else 0
                res_list = []
                for idx in range(st.session_state[ck]):
                    iv = default_value[idx] if isinstance(default_value, list) and idx < len(default_value) else {}
                    res_list.append(pydantic_form(it, key_prefix=f"{widget_key}_{idx}", initial_data=iv, asset_mgr=asset_mgr))
                data[field_name] = res_list

    render_logic(top_keys)
    if other_keys:
        st.markdown("---")
        with st.container(border=True):
            st.markdown("#### 🛠️ Advanced Settings")
            render_logic(other_keys)
    return data
