import json

class PermissionsConfiguration():

	def __init__(self, is_registration_required=True):
		if type(is_registration_required) != bool:
			raise TypeError((
				"'is_registration_required' argument during instance creattion "
				"must be of boolean type"
				" - '%s' (%s) detected"
			) % (is_registration_required, type(is_registration_required)))
		else:
			self.__registered_parameters = dict(
				roles=set(),
				users=set(),
				actions=set(),
				conditions=set(),
			)
			self.__privileges = dict(
				for_users=dict(),
				for_roles=dict(),
			)
			self.__options = dict(
				is_registration_required=is_registration_required
			)

	###############################################################
	###############################################################
	# dump and load 
	###############################################################
	###############################################################

	def dumps(self):
		return json.dumps(dict(
			registered_parameters=dict(
				roles=list(self.__registered_parameters['roles']),
				users=list(self.__registered_parameters['users']),
				actions=list(self.__registered_parameters['actions']),
				conditions=list(self.__registered_parameters['conditions']),
			),
			privileges=self.__privileges,
			options=self.__options,
		))

	def loads(self, dump_string):
		try:
			dump_dict = json.loads(dump_string)
		except ValueError as error:
			error.args = ((
				"Invalid JSON format while loading PermissionsConfiguration from a dump_string"
			),)
			raise
		else:
			# keep a backup of current state before starting to mangle the current state with __load()
			backup_dump_dict = json.loads(self.dumps())
			try:
				self.__load(dump_dict)
			except KeyError as error:
				self.__load(backup_dump_dict)
				raise

	def __load(self, dump_dict):
		self.__registered_parameters['roles'] = set(dump_dict['registered_parameters'].pop("roles"))
		self.__registered_parameters['users'] = set(dump_dict['registered_parameters'].pop("users"))
		self.__registered_parameters['actions'] = set(dump_dict['registered_parameters'].pop("actions"))
		self.__registered_parameters['conditions'] = set(dump_dict['registered_parameters'].pop("conditions"))
		if len(dump_dict['registered_parameters']) > 0:
			raise KeyError((
				"Unknown keys %s found to be registered inside dump dictionary"
			) % dump_dict['registered_parameters'].keys())
		else:
			dump_dict.pop("registered_parameters")
			self.__privileges = dump_dict.pop("privileges")
			self.__options = dump_dict.pop("options")
			if len(dump_dict) > 0:
				raise KeyError("Unknown keys %s found in dump dictionary" % dump_dict.keys())

	###############################################################
	###############################################################
	# registrations
	###############################################################
	###############################################################

	def is_registration_required(self, is_registration_required=None):
		if is_registration_required != None:
			# set a boolean value
			if type(is_registration_required) != bool:
				raise TypeError((
					"'is_registration_required' argument must be of boolean type"
					" - '%s' (%s) detected"
				) % (is_registration_required, type(is_registration_required)))
			else:
				self.__options['is_registration_required'] = is_registration_required
		else:
			# return the current value
			return self.__options['is_registration_required']

	def register_roles(self, *args):
		for index, a_role in enumerate(args):
			if type(a_role) != str:
				raise TypeError((
					"%dth role (%s) for registering roles must be a string - '%s' detected"
				) % (index, a_role, type(a_role)))
			else:
				self.__registered_parameters['roles'].add(a_role)

	def register_users(self, *args):
		for index, a_user in enumerate(args):
			if type(a_user) != str:
				raise TypeError((
					"%dth user (%s) for registering users must be a string - '%s' detected"
				) % (index, a_user, type(a_user)))
			else:
				self.__registered_parameters['users'].add(a_user)

	def register_actions(self, *args):
		for index, an_action in enumerate(args):
			if type(an_action) != str:
				raise TypeError((
					"%dth action (%s) for registering actions must be a string - '%s' detected"
				) % (index, an_action, type(an_action)))
			else:
				self.__registered_parameters['actions'].add(an_action)

	def register_conditions(self, *args):
		for index, a_condition in enumerate(args):
			if type(a_condition) != str:
				raise TypeError((
					"%dth condition (%s) for registering conditions must be a string - '%s' detected"
				) % (index, a_condition, type(a_condition)))
			else:
				self.__registered_parameters['conditions'].add(a_condition)

	###############################################################
	###############################################################
	# assigning privileges
	###############################################################
	###############################################################

	def assign_privilege_for_a_role(self, a_role, an_action, is_allowed_or_required_condition):
		self.__validate_parameters(
			a_role=a_role, an_action=an_action, 
			is_allowed_or_required_condition=is_allowed_or_required_condition
		)
		self.__privileges['for_roles'].setdefault(a_role, dict())
		self.__privileges['for_roles'][a_role][an_action] = is_allowed_or_required_condition

	def assign_privilege_for_a_user(self, a_user, an_action, is_allowed_or_required_condition):
		self.__validate_parameters(
			a_user=a_user, an_action=an_action, 
			is_allowed_or_required_condition=is_allowed_or_required_condition
		)
		self.__privileges['for_users'].setdefault(a_user, dict())
		self.__privileges['for_users'][a_user][an_action] = is_allowed_or_required_condition

	def unassign_privilege_for_a_role(self, a_role, an_action):
		try:
			self.__privileges['for_roles'][a_role].pop(an_action)
		except KeyError:
			raise LookupError((
				"Cannot unassign privilege"
				" - no action '%s' currently configured for role '%s'"
			) % (an_action, a_role))
		else:
			if len(self.__privileges['for_roles'][a_role]) == 0:
				self.__privileges['for_roles'].pop(a_role)

	def unassign_privilege_for_a_user(self, a_user, an_action):
		try:
			self.__privileges['for_users'][a_user].pop(an_action)
		except KeyError:
			raise LookupError((
				"Cannot unassign privilege"
				" - no action '%s' currently configured for user '%s'"
			) % (an_action, a_user))
		else:
			if len(self.__privileges['for_users'][a_user]) == 0:
				self.__privileges['for_users'].pop(a_user)

	def __validate_parameters(self,
		is_allowed_or_required_condition, a_role=None, a_user=None, an_action=None
	):
		if type(is_allowed_or_required_condition) != bool:
			# must be a string representing a required condition
			if not isinstance(is_allowed_or_required_condition, basestring):
				raise TypeError((
					"is_allowed_or_required_condition must be either a boolean or a string"
					" - '%s' (%s) detected"
				) % (is_allowed_or_required_condition, type(is_allowed_or_required_condition)))
			else:
				if self.is_registration_required():
					if is_allowed_or_required_condition not in list(self.__registered_parameters['conditions']):
						raise LookupError((
							"Condition '%s' is not yet registered in this configuration"
							" - must use a boolean or a registered string condition."
						) % (is_allowed_or_required_condition))

		if self.is_registration_required():
			if a_role and (a_role not in list(self.__registered_parameters['roles'])):
				raise LookupError("Role '%s' is not yet registered in this configuration" % a_role)

			if a_user and (a_user not in list(self.__registered_parameters['users'])):
				raise LookupError("User '%s' is not yet registered in this configuration" % a_user)

			if an_action and (an_action not in list(self.__registered_parameters['actions'])):
				raise LookupError("Action '%s' is not yet registered in this configuration" % an_action)

	###############################################################
	###############################################################
	# determining privileges
	###############################################################
	###############################################################

	def is_allowed(self, invoker_role, invoker_user, requested_action):
		# Recommended for simple use cases where no comlpex conditions are involved
		# May return either a True or a False
		is_allowed_or_required_condition = self.is_allowed_or_required_condition(
			invoker_role, invoker_user, requested_action
		)
		if type(is_allowed_or_required_condition) == bool:
			return is_allowed_or_required_condition
		else:
			raise TypeError((
				"Looks like a condition is involved here. "
				"Use the 'is_allowed_or_required_condition()' method instead"
			))

	def is_allowed_or_required_condition(self, invoker_role, invoker_user, requested_action):
		# Recommended for robust use cases where conditions may be involved
		# May return boolean True/False, or may return a string representing a condition
		try:
			return self.__privileges['for_users'][invoker_user][requested_action]
		except KeyError:
			try:
				return self.__privileges['for_roles'][invoker_role][requested_action]
			except KeyError:
				return False



