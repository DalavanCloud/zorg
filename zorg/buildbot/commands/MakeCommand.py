from buildbot.process.properties import WithProperties
from buildbot.steps.shell import WarningCountingShellCommand

class MakeCommand(WarningCountingShellCommand):

    @staticmethod
    def sanitize_kwargs(kwargs):
        # kwargs we could get and must not pass through
        # to the buildstep.RemoteShellCommand constructor.
        # Note: This is a workaround of the buildbot design issue,
        # thus should be removed once the original issue gets fixed.
        consume_kwargs = [
                             "jobs",
                         ]

        sanitized_kwargs = kwargs.copy()
        for k in consume_kwargs:
            if k in sanitized_kwargs.keys():
                del sanitized_kwargs[k]

        return sanitized_kwargs


    def __init__(self, prefixCommand=None, options=None, targets=None, **kwargs):
        self.prefixCommand = prefixCommand
        self.targets = targets

        if options is None:
            self.options = list()
        else:
            self.options = list(options)

        if kwargs.get('jobs', None):
             self.options += ["-j", kwargs['jobs']]
        else:
             self.options += [
                 WithProperties("%(jobs:+-j)s"),
                 WithProperties("%(jobs:-)s"),
                 ]

        command = []
        if prefixCommand:
            command += prefixCommand

        command += ["make"]

        if self.options:
            command += self.options

        if targets:
            command += targets

        # Remove here all the kwargs any of our LLVM buildbot command could consume.
        # Note: We will remove all the empty items from the command at start, as we
        # still didn't get yet WithProperties rendered.
        sanitized_kwargs = self.sanitize_kwargs(kwargs)

        sanitized_kwargs["command"] = command

        # And upcall to let the base class do its work
        WarningCountingShellCommand.__init__(self, **sanitized_kwargs)

        self.addFactoryArguments(prefixCommand=prefixCommand,
                                 options=self.options,
                                 targets=targets)


    def start(self):
        # Don't forget to remove all the empty items from the command,
        # which we could get because of WithProperties rendered as empty strings.
        self.command = filter(bool, self.command)
        # Then upcall.
        WarningCountingShellCommand.start(self)
