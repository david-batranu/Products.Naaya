
defaults = {'title': 'LDAP User Folder',
            'server': 'localhost:389',
            'login_attr': 'uid',
            'uid_attr': 'uid',
            'rdn_attr': 'uid',
            'users_base': 'ou=people,dc=dataflake,dc=org',
            'users_scope': 2,
            'roles': 'Anonymous',
            'groups_base': 'ou=groups,dc=dataflake,dc=org',
            'groups_scope': 2,
            'binduid': 'uid=Manager,dc=dataflake,dc=org',
            'bindpwd': 'mypass',
            'binduid_usage': 1,
            'local_groups': 0,
            'implicit_mapping': 0,
            'use_ssl': 0,
            'encryption': 'SHA',
            'read_only': 0,
            'extra_user_filter': ''}

alternates = {'title': 'LDAPUserFolder',
              'server': 'localhost:1389',
              'login_attr': 'uid',
              'uid_attr': 'uid',
              'users_base': 'ou=people,dc=type4,dc=org',
              'users_scope': 0,
              'roles': 'Anonymous, SpecialRole',
              'groups_base': 'ou=groups,dc=type4,dc=org',
              'groups_scope': 0,
              'binduid': 'cn=Manager,dc=type4,dc=org',
              'bindpwd': 'testpass',
              'binduid_usage': 2,
              'rdn_attr': 'uid',
              'local_groups': 1,
              'implicit_mapping': 0,
              'use_ssl': 1,
              'encryption': 'SSHA',
              'read_only': 1,
              'obj_classes': 'top, person, inetOrgPerson',
              'extra_user_filter': '(special=true)'}

satellite_defaults= {'title': 'Satellite',
                     'luf': '/luftest/acl_users',
                     'recurse': 0,
                     'groups_base': 'ou=special,dc=dataflake,dc=org',
                     'groups_scope': 2}

schema = {'uid': {'binary': False,
                  'friendly_name': 'uid',
                  'ldap_name': 'uid',
                  'multivalued': False,
                  'public_name': ''},
          'cn': {'binary': False,
                 'friendly_name': 'Canonical Name',
                 'ldap_name': 'cn',
                 'multivalued': False,
                 'public_name': ''},
          'sn': {'binary': False,
                 'friendly_name': 'Last name',
                 'ldap_name': 'sn',
                 'multivalued': False,
                 'public_name': 'lastname'},
          'givenName': {'binary': False,
                        'friendly_name': 'First name',
                        'ldap_name': 'givenName',
                        'multivalued': False,
                        'public_name': 'firstname'},
          'mail': {'binary': False,
                   'friendly_name': '',
                   'ldap_name': 'mail',
                   'multivalued': False,
                   'public_name': 'mail'},
          'o': {'binary': False,
                'friendly_name': 'organisationName',
                'ldap_name': 'o',
                'multivalued': False,
                'public_name': ''},
          'telephoneNumber': {'binary': False,
                              'friendly_name': 'Phone Number',
                              'ldap_name': 'telephoneNumber',
                              'multivalued': False,
                              'public_name': ''},
          'postalAddress': {'binary': False,
                            'friendly_name': '',
                            'ldap_name': 'postalAddress',
                            'multivalued': False,
                            'public_name': ''}}

user = {'uid': 'test',
        'cn': 'test',
        'sn': 'User',
        'mail': 'joe@blow.com',
        'givenName': 'G\xc3\xbcnther',
        'objectClasses': ['top', 'person'],
        'user_pw': 'mypass',
        'confirm_pw': 'mypass',
        'user_roles': ['Manager'],
        'mapped_attrs': {'objectClasses': 'Objektklassen'},
        'multivalued_attrs': ['objectClasses'],
        'ldap_groups': ['Group1', 'Group2']}

manager_user = {'uid': 'admin',
                'cn': 'admin',
                'sn': 'Manager',
                'givenName': 'Test',
                'user_pw': 'mypass',
                'confirm_pw': 'mypass',
                'user_roles': ['Manager', 'Administrator'],
                'ldap_groups': ['Group3', 'Group4']}

user2 = {'uid': 'test2',
         'cn': 'test2',
         'sn': 'User2',
         'mail': 'joe2@blow.com',
         'givenName': 'Test2',
         'objectClasses': ['top', 'posixAccount'],
         'user_pw': 'mypass',
         'confirm_pw': 'mypass',
         'user_roles': ['Manager'],
         'mapped_attrs': {'objectClasses': 'Objektklassen'},
         'multivalued_attrs': ['objectClasses'],
         'ldap_groups': ['Group1', 'Group2']}
