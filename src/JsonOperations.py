import json
import re

class JsonOperations:
    """
    Constructor
    """
    def __init__(self):
        self.jsonContent = ""
        self.lstCollections = []
 
    """
    Converts a dictionary of Java class definitions into a JSON schema 
    format.
    Parameters :
        java_dict (dict): A dictionary where keys are class names and values 
                          are strings containing Java class definitions
    Returns :
        str: A JSON string representing the schema of the Java classes
    """
    def java_dict_to_json_schema_withoutllm(self, java_dict, file_to_repo=None):
        # class_map key: "repo-name_ClassName" to avoid collisions across repos
        class_map = {}           # {qualified_key: code}
        simple_to_qualified = {} # {simple_class_name: set of all qualified_keys}
        collection_map = {}      # {qualified_key: qualified_key}
        lstCollection = []

        for path, code in java_dict.items():
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                class_name = class_match.group(1)
                repo_name = file_to_repo.get(path, '') if file_to_repo else ''
                qualified_key = f"{repo_name}_{class_name}" if repo_name else class_name
                class_map[qualified_key] = code
                # Track ALL qualified keys per simple name for repo-aware resolution
                if class_name not in simple_to_qualified:
                    simple_to_qualified[class_name] = set()
                simple_to_qualified[class_name].add(qualified_key)
                if '@Document(' in code:
                    collection_map[qualified_key] = qualified_key

        def get_repo_from_qualified(qualified_key, java_code):
            """Extract repo name from qualified_key by stripping '_ClassName' suffix."""
            class_match = re.search(r'class\s+(\w+)', java_code)
            if class_match:
                class_name = class_match.group(1)
                suffix = f'_{class_name}'
                if qualified_key.endswith(suffix):
                    return qualified_key[:-len(suffix)]
            return ''

        def resolve_type(simple_name, current_repo):
            """
            Resolve a simple Java type name to its qualified key.
            Prefers the class from the same repo as the declaring class.
            Falls back to any available qualified key (sorted for determinism).
            """
            candidates = simple_to_qualified.get(simple_name, set())
            if not candidates:
                return None
            same_repo_key = f"{current_repo}_{simple_name}" if current_repo else simple_name
            if same_repo_key in candidates:
                return same_repo_key
            # Fall back to first available (sorted for determinism)
            return sorted(candidates)[0]

        # Build parent map: qualified_key -> qualified_parent_key (repo-aware)
        parent_map = {}
        for qualified_key, code in class_map.items():
            parent_match = re.search(r'class\s+\w+\s+extends\s+(\w+)', code)
            if parent_match:
                parent_simple = parent_match.group(1)
                repo_name = get_repo_from_qualified(qualified_key, code)
                parent_qualified = resolve_type(parent_simple, repo_name)
                if parent_qualified:
                    parent_map[qualified_key] = parent_qualified

        def get_all_ancestor_fields(qualified_key, visited=None):
            """
            Walks the full inheritance chain bottom-up and collects all fields
            following Java rules:
              - A class's OWN declared fields (any access modifier) are always included.
              - From parent classes, fields with 'public' or 'protected' access are
                inherited; 'private' fields of a parent are NOT directly accessible in
                the child but ARE part of the serialised object state, so they are also
                included here (consistent with how Jackson / MongoDB reflection works).
              - The order is: grandparent fields -> parent fields -> own fields,
                so that child declarations shadow parents with the same name.
            """
            if visited is None:
                visited = set()
            if qualified_key in visited or qualified_key not in class_map:
                return {}
            visited.add(qualified_key)

            own_properties = {}
            inherited_properties = {}

            # --- Step 1: collect own declared fields first ---
            java_code = class_map[qualified_key]
            # Derive current repo for same-repo-first resolution
            current_repo = get_repo_from_qualified(qualified_key, java_code)
            raw_fields = re.findall(r'(private|protected|public)?\s*([\w<>\[\]]+)\s+(\w+)\s*;', java_code)
            for modifier, field_type, field_name in raw_fields:
                # Skip static / constant fields captured by the regex heuristic
                if field_name[0].isupper():
                    continue

                array_match = re.match(r'List<([\w]+)>', field_type)
                if array_match:
                    item_type = array_match.group(1)
                    item_qualified = resolve_type(item_type, current_repo)
                    if item_qualified and item_qualified in class_map:
                        item_schema = {
                            "type": "object",
                            "title": item_qualified,
                            "properties": get_all_ancestor_fields(item_qualified, visited.copy())
                        }
                    else:
                        item_schema = {"type": "string"}
                    own_properties[field_name] = {
                        "type": "array",
                        "items": item_schema
                    }
                else:
                    field_qualified = resolve_type(field_type, current_repo)
                    if field_qualified and field_qualified in class_map:
                        own_properties[field_name] = {
                            "type": "object",
                            "title": field_qualified,
                            "properties": get_all_ancestor_fields(field_qualified, visited.copy())
                        }
                    elif field_type in ('String', 'OffsetDateTime'):
                        own_properties[field_name] = {"type": "string"}
                    elif field_type in ('int', 'long', 'float', 'double',
                                        'Integer', 'Long', 'Float', 'Double'):
                        own_properties[field_name] = {"type": "number"}
                    elif field_type in ('boolean', 'Boolean'):
                        own_properties[field_name] = {"type": "boolean"}
                    else:
                        own_properties[field_name] = {"type": "string"}

            # --- Step 2: collect ancestor fields and append at the end ---
            if qualified_key in parent_map:
                parent_qualified = parent_map[qualified_key]
                # Use .copy() so sibling branches don't block each other
                parent_props = get_all_ancestor_fields(parent_qualified, visited.copy())
                # Only include inherited fields not already declared in the child
                for k, v in parent_props.items():
                    if k not in own_properties:
                        inherited_properties[k] = v

            # Own fields first, inherited fields last
            properties = {}
            properties.update(own_properties)
            properties.update(inherited_properties)

            return properties

        schemas = {}
        for qualified_key, java_code in class_map.items():
            schema_obj = {
                "type": "object",
                "description": "",
                "properties": get_all_ancestor_fields(qualified_key, set())
            }
            # Add x-collection-name if annotation is present
            if qualified_key in collection_map:
                schema_obj["x-collection-name"] = qualified_key
                lstCollection.append(qualified_key)
            schemas[qualified_key] = schema_obj

        result = {
            "components": {
                "schemas": schemas
            }
        }
        self.jsonContent = json.dumps(result, indent=None)
        self.lstCollections = lstCollection
        return self.jsonContent 

