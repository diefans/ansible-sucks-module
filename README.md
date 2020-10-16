# ansible-sucks-module

This ansible module serves as an anti-sucking tool to help developers maintain their mental integrity when forced to work with ansible.


# Features

Enables the developer to avoid the most crazy driving ansible feature: using jinja2 substitution to construct meaningful data structures from facts and back to facts.


# Background

Ansible seemes nice, but only for simple stuff like provisioning. When you have to maintain complex setups, you inevitably have to deal with ansible facts, the inventory and transformation of those into tool specific configurations and data structures.

Finally you force yourself registering a lot of _intermediate_ variables, [looping](https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html) over those and using a lot of [jinja filters](https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters.html). Your transformation becomes a distributed incomprehensible nightmare.

If you return a little later and try to make a sense out of it, you find yourself cursing and your head gets smashed by the pure insanity under which you subjugated yourself. Ansible is a monster eating the soul of every brave developer - if you ever had a chance to review the ansible code, you know you are fighting the devil <sup>[1](#pathtohell)</sup>.


# Internals

Basically this module executes a python code block via `exec`. You can provide `locals` to it. If you want to register the result, use `set_result(**kwargs)` if you want to create some facts use `set_facts(**kwargs)`

```python
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
```

# Usage

Clone the project and add the project path to `ANSIBLE_LIBRARY` or define `library` accordingly in `ansible.cfg` (see [docs](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#default-module-path)).

```yaml
- name: Get database IPs
  run_once: yes
  delegate_to: localhost
  py:
    locals:
      names: "{{ groups['database'] }}"
    code: |
      import socket
      ips = [socket.gethostbyname(name) for name in names]
      set_facts(database_ips=ips)

- debug:
    var: database_ips
```

<sub><a name="pathtohell">1</a>: Der Pfad zur Hölle ist gepflastert mit guten Absichten.</sub>
