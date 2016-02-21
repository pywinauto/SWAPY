# Code manager/generator.
# Copyright (C) 2016 Matiychuk D.
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

"""Code manager/generator."""


from abc import ABCMeta, abstractproperty
import re


def check_valid_identifier(identifier):
    """
    Check the identifier is a valid Python identifier.

    Since the identifier will be used as an attribute,
    don't check for reserved names.
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

    INIT_SNIPPET = 1
    ACTION_SNIPPET = 2

    def __init__(self, owner, init_code='', action_code='', close_code='',
                 indent=False):
        """Init code snippet."""
        if not init_code and not action_code and not close_code:
            raise SyntaxError("At least one of init_code, "
                              "action_code, close_code should be passed.")
        self.init_code = init_code
        self.action_code = action_code
        self.close_code = close_code
        self.indent = indent
        self.owner = owner

    def update(self, init_code=None, action_code=None, close_code=None,
               indent=None):
        """
        Update code.

        Updates only passed the args.
        To clear a code use empty line. For instance
        .update(init_code='new init code',
                action_code='')  # Erase old action_code
        """
        if init_code is not None:
            self.init_code = init_code

        if action_code is not None:
            self.action_code = action_code

        if close_code is not None:
            self.close_code = close_code

        if indent is not None:
            self.indent = indent

    @property
    def types(self):
        r"""Return mask with INIT_SNIPPET and\or ACTION_SNIPPET flags."""
        mask = 0
        if self.init_code or self.close_code:
            mask |= self.INIT_SNIPPET
        if self.action_code:
            mask |= self.ACTION_SNIPPET
        return mask

    def __repr__(self):
        """Convert code snippet to a string."""
        lines = []
        for code in ("init_code: %s" % self.init_code,
                     "action_code: %s" % self.action_code,
                     "close_code: %s" % self.close_code):
            lines.append(code)
        lines.append('-'*40)
        return '\n'.join(lines)


class CodeManager(object):
    """
    Manages code snippets.

    Handles intent if needed and keeps `close_code`
    always at the end. Single instance.
    """

    single_object = None
    inited = False

    def __new__(cls, *args, **kwargs):
        """
        Create code manager.

        Singletone.
        """
        if cls.single_object is None:
            new = super(CodeManager, cls).__new__(cls, *args, **kwargs)
            cls.single_object = new
            return new
        else:
            return cls.single_object

    def __init__(self, indent_symbols=' '*4):
        """Init code manager."""
        if not self.inited:
            self.snippets = []
            self.indent_symbols = indent_symbols

            self.inited = True

    def __len__(self):
        """Count code snippets."""
        return len(self.snippets)

    def _line(self, code, indent_count=0):
        return "{indents}{code}".format(
            indents=self.indent_symbols * indent_count,
            code=code)

    def add(self, snippet):
        """Add new code snippet."""
        self.snippets.append(snippet)

    def clear(self):
        """Safely clear all the snippents. Reset all the code counters."""
        while self.snippets:
            self.clear_last()

    def clear_last(self):
        """
        Clear last code.

        Remove the latest snippet, decrease appropriate code counter
        for snippets of INIT type.
        """
        if self.snippets:
            last_snippet = self.snippets.pop()
            if last_snippet.types & CodeSnippet.INIT_SNIPPET:
                last_snippet.owner.release_variable()

    def get_full_code(self):
        """Compose complete code from the snippets."""
        lines = []
        endings = []
        indent_count = 0
        for snippet in self.snippets:
            if snippet.init_code:
                lines.append(self._line(snippet.init_code, indent_count))

            if snippet.indent:
                # Add indent if needed. Notice the indent does not affect the
                # init_code in this iteration.
                indent_count += 1

            if snippet.action_code:
                lines.append(self._line(snippet.action_code, indent_count))

            if snippet.close_code:
                endings.append(self._line(snippet.close_code, indent_count))

        # Add the close_code codes.
        # Reverse the list for a close_code from the first snippet was passed
        # at the end of the code.
        if lines:
            full_code = "\n".join(lines)
            full_code += 2*"\n"
            full_code += "\n".join(endings[::-1])
        else:
            full_code = ""
        return full_code

    def get_init_snippet(self, owner):
        """Return the owner's the first INIT snippet."""
        for snippet in self.snippets:
            if snippet.owner == owner and \
                    snippet.types & CodeSnippet.INIT_SNIPPET:
                return snippet
        else:
            return None

    def __repr__(self):
        """Convert all code to a string."""
        return self.get_full_code()


class CodeGenerator(object):
    """
    Code generation behavior.

    Expect be used as one of base classes of the
    SWAPYObject's wrapper.
    """

    __metaclass__ = ABCMeta

    code_manager = CodeManager()
    code_var_name = None  # Default value, will be rewrote with composed
    # variable name as an instance attribute.

    code_var_counters = {}  # Default value, will be rewrote as instance's
    # class attribute by get_code_id(cls)

    @abstractproperty
    def _code_self(self):
        """Must compose self code."""
        pass

    @abstractproperty
    def code_var_pattern(self):
        """Must compose variable prefix."""
        pass

    @abstractproperty
    def code_parents(self):
        """Must contain all code parents chain."""
        pass

    @abstractproperty
    def direct_parent(self):
        """Must contain the nearest code parent."""
        pass

    @abstractproperty
    def _code_action(self):
        """Must contain action code."""
        pass

    @abstractproperty
    def _code_close(self):
        """Must contain close code."""
        pass

    @abstractproperty
    def code_var_pattern(self):
        """
        Abstractproperty.

        Must compose variable prefix, based on the control Class or
        short name of the SWAPY wrapper class.
        """
        pass

    @classmethod
    def get_code_id(cls, var_prefix='default'):
        """
        Increment code id.

        For example, the script already has
        `button1=...` line, so for a new button make `button2=... code`.
        The idea is the CodeGenerator's default value
        code_var_counters['var_prefix'] will be overwrote by this funk
        as a control's wrapper class(e.g Pwa_window) attribute.
        Its non default value will be shared for all the control's wrapper
        class(e.g Pwa_window) instances.
        """
        if var_prefix not in cls.code_var_counters or \
                cls.code_var_counters[var_prefix] == 0:
            cls.code_var_counters[var_prefix] = 1
            return ''  # "app=..." instead of "app1=..."

        else:
            cls.code_var_counters[var_prefix] += 1
            return cls.code_var_counters[var_prefix]

    @classmethod
    def decrement_code_id(cls, var_prefix='default'):
        """Decrement code id."""
        cls.code_var_counters[var_prefix] -= 1

    def get_code_self(self):
        r"""
        Self code.

        Composes code to access the control.
        E. g.: `button1 = calcframe1['Button12']`
        Pattern may use the next argument:
        * {var}
        * {parent_var}
        * {main_parent_var}
        E. g.: `"{var} = {parent_var}['access_name']\n"`.
        """
        pattern = self._code_self
        if pattern:
            if self.code_var_name is None:
                self.code_var_name = self.code_var_pattern.format(
                    id=self.get_code_id(self.code_var_pattern))

            format_kwargs = {'var': self.code_var_name}
            try:
                main_parent = self.code_parents[0]
            except IndexError:
                main_parent = None

            if self.direct_parent or main_parent:
                if self.direct_parent:
                    format_kwargs[
                        'parent_var'] = self.direct_parent.code_var_name
                if main_parent:
                    format_kwargs[
                        'main_parent_var'] = main_parent.code_var_name
            return pattern.format(**format_kwargs)
        return ""

    def get_code_action(self, action):
        r"""
        Action code.

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
        if self.direct_parent:
            format_kwargs['parent_var'] = self.direct_parent.code_var_name

        try:
            main_parent = self.code_parents[0]
        except IndexError:
            main_parent = None

        if main_parent:
            format_kwargs['main_parent_var'] = main_parent.code_var_name

        return self._code_action.format(**format_kwargs)

    def get_code_close(self):
        r"""
        Close code.

        Composes code to close the access to the control. E.g.: `app.Kill_()`
        Pattern may use the next argument:
        * {var}
        * {parent_var}
        * {main_parent_var}
        E. g.: `"{var}.Kill_()\n"`.
        """
        pattern = self._code_close
        if pattern:
            format_kwargs = {'var': self.code_var_name}
            if self.direct_parent:
                format_kwargs['parent_var'] = self.direct_parent.code_var_name

            try:
                main_parent = self.code_parents[0]
            except IndexError:
                main_parent = None

            if main_parent:
                format_kwargs['main_parent_var'] = main_parent.code_var_name

            return pattern.format(**format_kwargs)
        return ""

    def Get_code(self, action=None):
        """
        Get all generated code.

        Return all the code needed to make the action on the control.
        Walk parents if needed.
        """
        # TODO: not sure this is a good place for the check
        if not self._check_existence():  # target does not exist
            raise Exception("Target object does not exist")

        if self.code_var_name is None:
            # parent/s code is not inited
            code_parents = self.code_parents[:]
            code_parents.reverse()  # start from the top level parent

            for p in code_parents:
                if not p.code_var_name:
                    p_code_self = p.get_code_self()
                    p_close_code = p.get_code_close()
                    if p_code_self or p_close_code:
                        parent_snippet = CodeSnippet(p,
                                                     init_code=p_code_self,
                                                     close_code=p_close_code)
                        self.code_manager.add(parent_snippet)

            own_code_self = self.get_code_self()
            own_close_code = self.get_code_close()
            # get_code_action call should be after the get_code_self call
            own_code_action = self.get_code_action(action) if action else ''

            if own_code_self or own_close_code or own_code_action:
                own_snippet = CodeSnippet(self,
                                          init_code=own_code_self,
                                          action_code=own_code_action,
                                          close_code=own_close_code)
                self.code_manager.add(own_snippet)
        else:
            # Already inited (all parents too), may use get_code_action
            own_code_action = self.get_code_action(action) if action else ''
            if own_code_action:
                new_action_snippet = CodeSnippet(self,
                                                 action_code=own_code_action)
                self.code_manager.add(new_action_snippet)

        return self.code_manager.get_full_code()

    def update_code_style(self):
        """
        Switch between code styles.

        Seeks for the first INIT snippet and update
        `init_code` and `close_code`.
        """
        init_code_snippet = self.code_manager.get_init_snippet(self)
        if init_code_snippet:
            own_code_self = self.get_code_self()
            own_close_code = self.get_code_close()
            if own_code_self or own_close_code:
                init_code_snippet.update(init_code=own_code_self,
                                         close_code=own_close_code)

    def release_variable(self):
        """
        Release variable in codegen.

        Clear the access variable to mark the object is not inited and
        make possible other use the variable name.
        """
        if self.code_var_name:
            self.code_var_name = None
            self.decrement_code_id(self.code_var_pattern)


if __name__ == '__main__':
    c1 = CodeSnippet(None, 'with Start_ as app:', 'frame1 = app.Frame', '',
                     True)
    c2 = CodeSnippet(None, 'button1 = frame1.button', 'button1.Click()',
                     'del button1')
    c3 = CodeSnippet(None, 'button2 = frame1.button', 'button2.Click()')
    c4 = CodeSnippet(None, 'with Start_ as app:', 'frame2 = app.Frame', '',
                     True)
    c5 = CodeSnippet(None, '', 'button1.Click()')
    cm = CodeManager()

    print c1
    [cm.add(i) for i in [c1, c2, c3, c4, c5]]

    print id(c2)
    print cm

    c2.update('button1 = the_change', 'the_change.Click()',
              'del the_change')
    print id(c2)
    print cm
