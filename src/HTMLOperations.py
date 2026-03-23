import json
import src.configurations as configurations
import re

class HTMLOperations:
    """
    Constructor
    """
    def __init__(self):
        self.htmlContent = ""
    """
    Generates HTML corresponding to a java class using resolved json schema
    """
    def generateHTML(self, jsonStr, class_name, logger=None):
        html = ""
        try:
            # Parse the JSON string if needed
            if isinstance(jsonStr, str):
                try:
                    schema = json.loads(jsonStr)
                except Exception:
                    schema = jsonStr  # fallback if already dict
            else:
                schema = jsonStr

            # ------------------------------------------------------------------
            # Build a global title -> properties map by scanning the entire JSON.
            # When the same title appears multiple times, keep the entry with the
            # most properties (i.e. the fully-resolved one).
            # ------------------------------------------------------------------
            title_map = {}

            def collect_titles(obj):
                if isinstance(obj, dict):
                    title = obj.get('title')
                    props = obj.get('properties')
                    if title and props:
                        # Prefer the definition that has more properties
                        if title not in title_map or len(props) > len(title_map[title]):
                            title_map[title] = props
                    for v in obj.values():
                        collect_titles(v)
                elif isinstance(obj, list):
                    for item in obj:
                        collect_titles(item)

            collect_titles(schema)

            # ------------------------------------------------------------------
            # Render a properties dict as an HTML table.
            # visited: set of class titles already being expanded on the current
            # render path — prevents infinite recursion on circular references.
            # Sibling branches each get their own visited copy so they can
            # independently expand the same class.
            # ------------------------------------------------------------------
            def render_table(properties, visited=None, descriptions=None):
                if visited is None:
                    visited = set()
                html = '''<table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;background:#f9f9f9;">
                <tr style="background:#4a90e2;color:#fff;">
                    <th style="padding:8px;border:1px solid #4a90e2;">Field Name</th>
                    <th style="padding:8px;border:1px solid #4a90e2;">Type</th>
                    <th style="padding:8px;border:1px solid #4a90e2;">Description</th>
                </tr>'''
                for idx, (field, prop) in enumerate(properties.items()):
                    field_type = prop.get('type', '')
                    desc = prop.get('description', '')
                    row_bg = '#eaf2fb' if idx % 2 == 0 else '#fff'
                    # Handle array of objects
                    if field_type == 'array' and 'items' in prop and isinstance(prop['items'], dict):
                        items_type = prop['items'].get('type', '')
                        if items_type == 'object':
                            array_title = prop['items'].get('title', 'objects')
                            # Use inline properties; fall back to title_map when empty
                            items_props = prop['items'].get('properties') or {}
                            if not items_props and array_title in title_map:
                                items_props = title_map[array_title]
                            if items_props and array_title not in visited:
                                macro_title = f'Array of {array_title}'
                                html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td>'
                                html += f'<td style="padding:8px;border:1px solid #4a90e2;">'
                                html += f'<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">{macro_title}</ac:parameter><ac:rich-text-body>'
                                html += render_table(items_props, visited | {array_title})
                                html += '</ac:rich-text-body></ac:structured-macro></td>'
                                html += f'<td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                            else:
                                # Cycle detected or no properties — show as plain array label
                                html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td><td style="padding:8px;border:1px solid #4a90e2;">Array of {array_title}</td><td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                        else:
                            # Array of primitives
                            html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td><td style="padding:8px;border:1px solid #4a90e2;">Array of {items_type}</td><td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                    # If type is object, render expand macro with inner table
                    elif field_type == 'object':
                        obj_title = prop.get('title', 'object')
                        # Use inline properties; fall back to title_map when empty
                        obj_props = prop.get('properties') or {}
                        if not obj_props and obj_title in title_map:
                            obj_props = title_map[obj_title]
                        if obj_props and obj_title not in visited:
                            html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td>'
                            html += f'<td style="padding:8px;border:1px solid #4a90e2;">'
                            html += f'<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">{obj_title}</ac:parameter><ac:rich-text-body>'
                            html += render_table(obj_props, visited | {obj_title})
                            html += '</ac:rich-text-body></ac:structured-macro></td>'
                            html += f'<td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                        else:
                            # Cycle detected or no properties — show type title as plain text
                            display = obj_title if obj_title else field_type
                            html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td><td style="padding:8px;border:1px solid #4a90e2;">{display}</td><td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                    else:
                        html += f'<tr style="background:{row_bg};"><td style="padding:8px;border:1px solid #4a90e2;">{field}</td><td style="padding:8px;border:1px solid #4a90e2;">{field_type}</td><td style="padding:8px;border:1px solid #4a90e2;">{desc}</td></tr>'
                html += '</table>'
                return html

            # Find the schema for the given collection/class name
            # If input is a dict of all schemas, get the right one
            if isinstance(schema, dict) and 'components' in schema and 'schemas' in schema['components']:
                schemas = schema['components']['schemas']
                if class_name in schemas:
                    target_schema = schemas[class_name]
                else:
                    # fallback: just pick the first
                    target_schema = next(iter(schemas.values()))
            elif isinstance(schema, dict) and class_name in schema:
                target_schema = schema[class_name]
            else:
                target_schema = schema

            # Render the main table with a bold heading for the class name
            class_heading = class_name if isinstance(class_name, str) else str(class_name)
            html = f'<div style="font-size:1.3em;font-weight:bold;margin-bottom:8px;">{class_heading}</div>'
            html += render_table(target_schema.get('properties', {}))
            return html
        except Exception as e:
            import traceback
            err_detail = traceback.format_exc()
            print(f"Error generating HTML for {class_name}: {e}\n{err_detail}")
            if logger:
                logger.write_log(f"ERROR generating HTML for {class_name}: {e}")
                logger.write_log(err_detail)
            return ""