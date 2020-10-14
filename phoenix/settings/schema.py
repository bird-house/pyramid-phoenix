import deform
from deform.widget import OptGroup
import colander

from phoenix.security import AUTH_PROTOCOLS

import logging
LOGGER = logging.getLogger("PHOENIX")


@colander.deferred
def deferred_processes_widget(node, kw):
    processes = kw.get('processes', [])
    choices = [('', "Select up to six public processes you'd like to show.")]
    for group in list(processes.keys()):
        options = []
        for process in processes[group]:
            option = "{}.{}".format(group, process)
            options.append((option, process))
        choices.append(OptGroup(group, *options))
    return deform.widget.Select2Widget(values=choices, multiple=True)


class ProcessesSchema(deform.schema.CSRFSchema):
    pinned_processes = colander.SchemaNode(
        colander.Set(),
        widget=deferred_processes_widget,
        validator=colander.Length(min=0, max=6)
    )


class AuthProtocolSchema(deform.schema.CSRFSchema):
    choices = list(AUTH_PROTOCOLS.items())

    auth_protocol = colander.SchemaNode(
        colander.Set(),
        default=['phoenix'],
        title='Authentication Protocol',
        description='Choose at least one Authentication Protocol which is used in Phoenix.',
        validator=colander.Length(min=1),
        widget=deform.widget.CheckboxChoiceWidget(values=choices, inline=True))
