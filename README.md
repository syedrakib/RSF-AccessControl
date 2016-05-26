# RSF-Pyrmissions

Ridiculously Straight Forward Permissioning system (aka Access Control) for python projects

**Install the package from PyPI** 

    pip install rsf-pyrmissions

**Import the package and create an object of `PermissionsConfiguration` class. We will call it `pc` for this documentation.**
    
    from rsf_pyrmissions.utils import PermissionsConfiguration
    pc = PermissionsConfiguration()

We could (optionally) pass in a boolean `is_registration_required` argument in this statement. However, for this quick demo purpose, we will keep it blank (which defaults to `False`) and, hence, remove such constraints for requiring registrations. 

However, for production purposes, it is highly recommended to set this value to `True`. We shall discuss its importance later.

# Setting privileges for roles and users

We will use random roles and users to assign privileges to them. Note that, there is nothing significant about what / how you call each role / user. It doesn't matter whether a role is called "superuser" or an "intern". The only thing that matters is which arbitrary string denoting a role has been assigned what kind of privileges for an arbitrary string of action. 

    # all managers can remove items
    a_role = "manager"
    an_action = "remove"
    is_allowed = True
    pc.assign_privilege_for_a_role(a_role, an_action, is_allowed)
    
    # no users can remove items
    a_role = "users"
    an_action = "remove"
    is_allowed = False
    pc.assign_privilege_for_a_role(a_role, an_action, is_allowed)
    
    # Alice can always remove items whether she is a manager or a user
    a_user = "alice"
    an_action = "remove"
    is_allowed = True
    pc.assign_privilege_for_a_user(a_user, an_action, is_allowed)
    
It's all arbitrary - you're free to call your roles, users, actions whatever you want. All these privilege assignments and rules have been saved inside the `pc` object. 

# Determining privileges for a role or a user
    
    a_role = "user"
    a_user = "alice"
    an_action = "remove"
    pc.is_allowed(a_role, a_user, an_action) # True
    
    a_role = None # maybe Alice was never even assigned any role in our project
    a_user = "alice"
    an_action = "remove"
    pc.is_allowed(a_role, a_user, an_action) # True

Let's take Bob for example. He is someone who hasn't been assigned any privileges yet.

	a_role = "user" # or could be None if we don't know his role in the project
	a_user = "bob"
	an_action = "remove"
	pc.is_allowed(a_role, a_user, an_action) # False
    
Bob as a user cannot remove items. But managers can. So, if Bob is promoted to become a manager
    
    a_role = "manager"
    a_user = "bob"
    an_action = "remove"
    pc.is_allowed(a_role, a_user, an_action) # True
    
Each of these fields (`a_role`, `a_user`, `an_action`) are compulsory for determining a privilege with `is_allowed()`. However, it is completely normal to leave one or more of these fields as `None` if its value is not known particularly. By default, if any role-user-action combination is used which was not previously assigned any privileges, then `False` will be returned
    
    a_role = "superuser" # superusers can destroy a universe
    a_user = "charlie" # charlie is the master maniac
    an_action = "smash_an_apple" 
    pc.is_allowed(a_role, a_user, an_action) # False - because these roles/users were never assigned any privilegs on the first place
    
# Fine-grain control with special conditions

So far, Alice can remove any item she wants whether she is user or manager. Bob cannot remove any item. But if he queries his privilege as a Manager then he can remove any item because the Manager role is allowed to remove items. 

Now, let's say we want to allow Bob to remove items but only those items which belong to him - not others. We can call this condition `"self_items"`. Again, any arbitrary string is accepted.

    a_user = "bob"
    an_action = "remove"
    is_allowed = True
    a_condition = "self_items"
    pc.assign_privilege_for_a_user(a_user, an_action, is_allowed, a_condition)

Notice that we had not used the `a_condition` field till now for assigning privileges previously - it is an optional field.

Now, let's say Bob is an intern (a role which has not been introduced to the `pc` object yet) and will be allowed to remove contents only if he includes the condition that he is trying to remove his own contents.

    a_role = "intern"
    a_user = "bob"
    an_action = "remove"
    known_condition = None
    pc.is_allowed(a_role, a_user, an_action) # False
    
    known_condition = "self_items"
    pc.is_allowed(a_role, a_user, an_action, known_condition) # True

Any user or any role can be permitted some actions based on some conditions. If conditions have been set but the conditions are not met, then `pc` object will return False.

# Requiring Registrations

Earlier in the docs above, we had skipped this topic and said it will be covered later. It is possible (and recommended) to enforce some constraints on the kinds of strings that can be used for assigining the roles, users, actions, conditions etc. Since these are just arbitrary strings, while assigning a privilege with a mistyped string parameter, it should raise an error and warn you instead of silently accepting it.

In order to prevent such situations, you can (rather, **you should**) turn on the `is_registration_required` option during object creation and register every expected string in one initialization space before actually using them or querying them later on.

    pc = PermissionsConfiguration(is_registration_required=True)
    # or simply
    pc = PermissionsConfiguration(True)

Or if you want to change this behavior later on

    pc.is_registration_required(True)
    # or 
    pc.is_registration_required(False)

You can query the value of its current state by simply passing no arguments at all

	pc.is_registration_required()

Register the strings that you expect will be used / needed in your project in the future

    pc.register_roles("manager", "user", "intern")
    pc.register_users("alice", "bob", "carl", "david")
    pc.register_actions("add", "remove", "edit")
    pc.register_conditions("self_items", "all_items")

Hence, later on if you try to assign a privilege with a mistyped parameter (or with a new parameter which has not yet been registered) it will raise an error. 

    pc.assign_privilege_for_a_role("superintern", "remove", True)
	# LookupError: Role 'superintern' is not yet registered in this configuration

    pc.assign_privilege_for_a_user("alice", "remov", True)
	# LookupError: Action 'remov' is not yet registered in this configuration

This helps in various cases where accounting / planning for newly introduced roles, users, actions (before using them) is important. **It is recommended to enforce this requirement in production applications.**

# Export / Import

**Export**

    from rsf_pyrmissions.utils import dump_configuration
    dump_string = dump_configuration(pc) # produces a long base64 encoded pickled string 

This string represents the state of the `pc` object and can be easily stored in a regular database, file system etc for retrieving later.

**Import**

	from rsf_pyrmissions.utils import load_configuration
	pc2 = load_configuration(dump_string)
	
This `pc2` object is now an exact replica of the original `pc` object that we first created. We can resume all assigning and querying operations on this new `pc2` object just like we were doing for the original `pc` object.

# A useful internal function

    pc.current_state() 

returns a json string of a dictionary representation of all the fields and attributes inside the object. This maybe helpful to inspect and review what has been set inside currently.
    
# Summary

- Any privilege that has been defined explicitly for a specific user, will override whatever role he/she is a part of - role of the user does not matter if an explicit privilege has been assigned to that user for the action
- A user (or a role) can be disallowed some actions while being allowed the same actions upon fulfilling certain known conditions
- A user (or a role) can also be allowed some actions while being disallowed the same actions under certain known conditions
- Whenever a combination of role/user/action/condition is used which is particularly unknown to the PermissionsConfiguration object, it will return `False` when queried with `is_allowed()`.
- There are no automatic heirarchies enforced in any way (such as manager can do whatever a user can, a user can do whatever an intern can etc). You are expected to set the privileges for every action for every role / user explicitly.

# Important note

RSF-Pyrmissions does not keep record of which user has which role, which role has higher privileges than other roles etc. When you use this library in your project, it is expected that your project will keep the important records of which user has which role and who is above whom and what not. Your project will determine which user is trying to perform what action, whether the user is fulfiling a condition or not etc. RSF-Pyrmissions will only let you know if `a_user` with `a_role` trying to perform `an_action` with `a_condition` (or without `a_condition`) is allowed to perform that action or not - simple, no strings attached, ridiculously straight forward.
    
    
    
    
    
    