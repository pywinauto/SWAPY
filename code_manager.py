# GUI object/properties browser.
# Copyright (C) 2015 Matiychuk D.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA


import re



def check_valid_identifier(identifier):

    """
    Check the identifier is a valid Python identifier.
    Since the identifier will be used as an attribute, don't check for reserved names.
    """

    return bool(re.match("[_A-Za-z][_a-zA-Z0-9]*$", identifier))


class CodeSnippet(object):

    """
    A piece of the code.
    `init_code` a code used one time in the beginning.
    `action_code` use already inited object.
    `close_code` a part passed to the end of the code.
    `indent` means `action_code` and `close_code` should be under the indent.
    """

    def __init__(self, init_code='', action_code='', close_code='', indent=False):
        if not init_code and not action_code and not close_code:
            raise SyntaxError("At least one of init_code, action_code, close_code should be passed.")
        self.init_code = init_code
        self.action_code = action_code
        self.close_code = close_code
        self.indent = indent

    def __repr__(self):
        lines = []
        for code in (self.init_code, self.action_code, self.close_code):
            lines.append(code)
        return '\n'.join(lines)


class CodeManager(object):

    """
    Manages code snippets. Handles intent if needed and keeps `close_code` always at the end.
    Single instance.
    """

    single_object = None

    def __new__(cls, *args, **kwargs):
        if cls.single_object:
            return cls.single_object
        else:
            new = super(CodeManager, cls).__new__(cls, *args, **kwargs)
            cls.single_object = new
            return new

    def __init__(self, indent_symbols=' '*4):
        self.snippets = []
        self.indent_symbols = indent_symbols

    def _line(self, code, indent_count=0):
        return "{indents}{code}".format(indents=self.indent_symbols * indent_count,
                                        code=code)

    def add(self, snippet):
        self.snippets.append(snippet)

    def clear(self):
        self.snippets = []

    def get_full_code(self):

        """
        Compose complete code from the snippets
        """

        lines = []
        endings = []
        indent_count = 0
        for snippet in self.snippets:
            if snippet.init_code:
                lines.append(self._line(snippet.init_code, indent_count))

            if snippet.indent:
                # Add indent if needed. Notice the indent does not affect the init_code in this iteration.
                indent_count += 1

            if snippet.action_code:
                lines.append(self._line(snippet.action_code, indent_count))

            if snippet.close_code:
                endings.append(self._line(snippet.close_code, indent_count))

        # Add the close_code codes.
        # Reverse the list for a close_code from the first snippet was passed at the end of the code.
        full_code = "\n".join(lines)
        full_code += 2*"\n"
        full_code += "\n".join(endings[::-1])
        return full_code

    def __repr__(self):
        return self.get_full_code()


class CodeGenerator(object):

    """
    Code generation behavior. Expect be used as one of base classes of the SWAPYObject's wrapper.
    """
    code_manager = CodeManager()
    code_var_name = None  # Default value, will be rewrote with composed variable name as an instance attribute.
    code_var_counters = {}  # Default value, will be rewrote as instance's class attribute by get_code_id(cls)

    @classmethod
    def get_code_id(cls, var_prefix='default'):

        """
        Increment code id. For example, the script already has `button1=...` line,
        so for a new button make `button2=... code`.
        The idea is the CodeGenerator's default value code_var_counters['var_prefix'] will be overwrote by this funk
        as a control's wrapper class(e.g Pwa_window) attribute.
        Its non default value will be shared for all the control's wrapper class(e.g Pwa_window) instances.
        """

        if var_prefix not in cls.code_var_counters:
            cls.code_var_counters[var_prefix] = 1
        else:
            cls.code_var_counters[var_prefix] += 1
        return cls.code_var_counters[var_prefix]

    def get_code_self(self):

        """
        Composes code to access the control. E. g.: `button1 = calcframe1['Button12']`
        Pattern may use the next argument:
        * {var}
        * {parent_var}
        * {main_parent_var}
        E. g.: `"{var} = {parent_var}['access_name']\n"`.
        """

        pattern = self._code_self
        if pattern:
            self.code_var_name = self.code_var_pattern.format(id=self.get_code_id(self.code_var_pattern))
            format_kwargs = {'var': self.code_var_name}
            try:
                main_parent = self.code_parents[0]
            except IndexError:
                main_parent = None

            if self.parent or main_parent:
                if self.parent:
                    format_kwargs['parent_var'] = self.parent.code_var_name
                if main_parent:
                    format_kwargs['main_parent_var'] = main_parent.code_var_name
            return pattern.format(**format_kwargs)
        return ""

    def get_code_action(self, action):

        """
        Composes code to run an action. E. g.: `button1.Click()`
        Pattern may use the next argument:
        * {var}
        * {action}
        * {parent_var}
        * {main_parent_var}
        E. g.: `"{var}.{action}()\n"`.
        """

        format_kwargs = {'var': self.code_var_name,
                         'action': action}
        if self.parent:
            format_kwargs['parent_var'] = self.parent.code_var_name

        if self.code_parents[0]:
            format_kwargs['main_parent_var'] = self.code_parents[0].code_var_name

        return self._code_action.format(**format_kwargs)

    def get_code_close(self):

        """
        Composes code to close the access to thethe control. E. g.: `app.Kill_()`
        Pattern may use the next argument:
        * {var}
        * {parent_var}
        * {main_parent_var}
        E. g.: `"{var}.Kill_()\n"`.
        """

        pattern = self._code_close
        if pattern:
            format_kwargs = {'var': self.code_var_name}
            if self.parent:
                format_kwargs['parent_var'] = self.parent.code_var_name

            if self.code_parents[0]:
                format_kwargs['main_parent_var'] = self.code_parents[0].code_var_name

            return pattern.format(**format_kwargs)
        return ""

    def Get_code(self, action=None):

        """
        Return all the code nneded to make the action on the control.
        Walk parents if needed.
        """

        #code = ""
        if self.code_var_name is None:
            # parent/s code is not inited
            code_parents = self.code_parents[:]
            code_parents.reverse()  # start from the top level parent

            for p in code_parents:
                if not p.code_var_name:
                    parent_init_code = p.get_code_self()
                    #code += parent_init_code
                    self.code_manager.add(CodeSnippet(init_code=parent_init_code,
                                                      close_code=p.get_code_close()))

            self_code_self = self.get_code_self()  # self access code
            #code += self_code_self
            self.code_manager.add(CodeSnippet(init_code=self_code_self,
                                              close_code=self.get_code_close()))
        if action:
            self_code_action = self.get_code_action(action)  # self action code
            #code += self_code_action
            self.code_manager.add(CodeSnippet(action_code=self_code_action))

        #print self.code_manager

        #return code
        return self.code_manager.get_full_code()


if __name__ == '__main__':
    c1 = CodeSnippet('with Start_ as app:', 'frame1 = app.Frame', '', True)
    c2 = CodeSnippet('button1 = frame1.button', 'button1.Click()', 'del button1')
    c3 = CodeSnippet('button2 = frame1.button', 'button2.Click()')
    c4 = CodeSnippet('with Start_ as app:', 'frame2 = app.Frame', '', True)
    c5 = CodeSnippet('', 'button1.Click()')
    cm = CodeManager()

    print c1
    [cm.add(i) for i in [c1, c2, c3, c4, c5]]

    print cm
