# #!/usr/bin/env python3
# """
# merge_overrides.py  –  Generate override-values.yaml for a new Helm chart
#                        while warning about brand-new keys.

# Usage
#   python merge_overrides.py \
#       -d values.yaml \
#       -r override-values.yaml \
#       -o override-values.generated.yaml
# """

# import argparse, sys, pathlib
# from ruamel.yaml import YAML
# from ruamel.yaml.comments import CommentedMap

# yaml = YAML()
# yaml.indent(mapping=2, sequence=4, offset=2)

# def load_yaml(path: pathlib.Path):
#     with path.open() as f:
#         return yaml.load(f)


# def recursive_merge(default, reference, path="", new_keys=None, extra_keys=None):
#     """
#     Recursively merge two nested YAML trees.
#     • Take the reference value wherever it exists.
#     • Otherwise keep the default value and record the key path in new_keys.
#     """
#     if new_keys is None:
#         new_keys = []

#     # ── Dictionaries ────────────────────────────────────────────────────
#     if isinstance(default, dict):
#         merged = CommentedMap()
#         for key, def_val in default.items():
#             cur_path = f"{path}.{key}" if path else key
#             if key in reference:
#                 merged[key] = recursive_merge(
#                     def_val, reference[key], cur_path, new_keys, extra_keys
#                 )
#             else:
#                 merged[key] = def_val
#                 new_keys.append(cur_path)
#         for key in reference:
#             if key not in default:
#                 cur_path = f"{path}.{key}" if path else key
#                 merged[key] = reference[key]
#                 if extra_keys is not None:
#                     extra_keys.append(cur_path)

#         return merged

#     # ── Leaf nodes ──────────────────────────────────────────────────────
#     return reference if reference is not None else default


# def main():
#     p = argparse.ArgumentParser()
#     p.add_argument("-d", "--default", required=True, type=pathlib.Path,
#                    help="values.yaml from the chart")
#     p.add_argument("-r", "--reference", required=True, type=pathlib.Path,
#                    help="previous override-values.yaml")
#     p.add_argument("-o", "--output", default="override-values.generated.yaml",
#                    type=pathlib.Path, help="merged YAML file to write")
#     args = p.parse_args()

#     default_yaml   = load_yaml(args.default)
#     reference_yaml = load_yaml(args.reference)

#     new_keys: list[str] = []
#     extra_keys: list[str] = []
#     merged = recursive_merge(default_yaml, reference_yaml, new_keys=new_keys, extra_keys=extra_keys)

#     with args.output.open("w") as f:
#         yaml.dump(merged, f)

#     print(f"\nMerged override written to {args.output}")
#     if new_keys:
#         print("\nNEW keys detected in the chart that were not in your "
#               "existing override:")
#         for k in sorted(new_keys):
#             print(f"  • {k}")
#         print("\nEdit the generated file and decide on values for those keys.")
#     else:
#         print("\nNo new keys detected – overrides fully cover the chart.")
#     if extra_keys:
#         print("\nEXTRA keys in your override that are not in the chart:")
#         for k in sorted(extra_keys):
#             print(f"  • {k}")
#         print("\nYou may want to remove those keys from your override file.")


# if __name__ == "__main__":
#     sys.exit(main())




















#!/usr/bin/env python3
"""
merge_overrides.py – Merge a fresh chart values.yaml with an existing
override-values.yaml and warn about

  • new keys that appear in the chart but not in the override
  • extra keys that appear in the override but no longer exist in the chart
"""

import argparse, pathlib, sys
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap   # ← changed

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def load_yaml(path: pathlib.Path):
    with path.open() as f:
        return yaml.load(f)


def recursive_merge(default, reference, path="",
                    new_keys=None, extra_keys=None):          # ← changed
    """depth-first merge + collect diff paths"""
    if new_keys is None:                                      # ← changed
        new_keys = []
    if extra_keys is None:                                    # ← changed
        extra_keys = []

    # ── dictionaries ────────────────────────────────────────────────
    if isinstance(default, dict):
        merged = CommentedMap()
        # pass 1 – keys that exist in chart defaults
        for key, def_val in default.items():
            cur = f"{path}.{key}" if path else key
            if key in reference:
                merged[key] = recursive_merge(def_val, reference[key],
                                              cur, new_keys, extra_keys)
            else:
                merged[key] = def_val
                new_keys.append(cur)
        # pass 2 – keys that exist only in the old override
        for key, ref_val in reference.items():
            if key not in default:
                cur = f"{path}.{key}" if path else key
                merged[key] = ref_val
                extra_keys.append(cur)
        return merged

    # ── leaf nodes ──────────────────────────────────────────────────
    return reference if reference is not None else default


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--default", required=True, type=pathlib.Path,
                   help="values.yaml from the new chart")
    p.add_argument("-r", "--reference", required=True, type=pathlib.Path,
                   help="previous override-values.yaml")
    p.add_argument("-o", "--output", default="override-values.generated.yaml",
                   type=pathlib.Path,
                   help="path to write merged override file")
    args = p.parse_args()

    default_yaml   = load_yaml(args.default)
    reference_yaml = load_yaml(args.reference)

    new_keys:   list[str] = []
    extra_keys: list[str] = []

    merged = recursive_merge(default_yaml, reference_yaml,
                             new_keys=new_keys, extra_keys=extra_keys)

    with args.output.open("w") as f:
        yaml.dump(merged, f)

    print(f"\nMerged override written to {args.output}")

    if new_keys:
        print(f"\nKeys that are **new in the chart** (only in values and not in {args.reference}):")
        for k in sorted(new_keys):
            print(f"  • {k}")

    if extra_keys:
        print(f"\nKeys that are **only in your old override** "
              f"(no longer in chart(values.yaml) {args.default}):")
        for k in sorted(extra_keys):
            print(f"  • {k}")

    if not new_keys and not extra_keys:
        print("\nOverride fully aligned – no new or obsolete keys.")


if __name__ == "__main__":
    sys.exit(main())


"""
values.yaml:
*************************************

---
parent1:
    child1:
        - arrayelement1
        - arrayelement2
    child2:
        subchild1:
            - dict1: false
              name: value1
    child3: "dummy_value"
    child4: ""

********************************************
override-values.yaml:
---
parent1:
    child1:
        - arrayelement1
        - arrayelement2
        - arrayelement3
    child2:
        subchild1:
            - dict1: true
              name: "subchild1_dict1"
    another_child: "dummy123"


****************************************
generated.yaml(output):
parent1:
  child1:
    - arrayelement1
    - arrayelement2
    - arrayelement3
  child2:
    subchild1:
      - dict1: true
        name: subchild1_dict1
  child3: dummy_value
  child4: ''
  another_child: dummy123


Usage: python merge-overrides.py -r orverride-values.yaml -d values.yaml -o generated.yaml
"""
