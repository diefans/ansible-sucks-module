#!/usr/bin/env python
# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <https://unlicense.org>
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
Run arbitrary Python code.
You may also set facts and result, via `set_facts(**kwargs)` and `set_result(**kwargs)`.

options:
    code:
        type: string
        required: True
    locals:
        type: dict
        required: False
"""


def run_module():
    module_args = {
        "code": {"type": "str", "required": True},
        "locals": {"type": "dict", "required": False, "default": {}},
    }
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    result = {}
    facts = {}
    _globals = {
        "set_result": result.update,
        "set_facts": facts.update,
        # copy locals, since ansible tries to clean it up afterwards, but fails
        # for e.g. imported modules
        **module.params["locals"],
    }
    code_object = compile(module.params["code"], "<string>", "exec")
    # imported names settle in locals, so we unite locals and globals, to have
    # them available
    exec(code_object, _globals, _globals)

    result["ansible_facts"] = facts
    module.exit_json(msg="Code executed", **result)


if __name__ == "__main__":
    run_module()
