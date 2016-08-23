<div class="btn-group" role="group">
  % for button in buttons:
  <% target = 'target="_blank"' if button.new_window else '' %>
  % if button.icon:
  <a class="${button.css_class}" data-toggle="tooltip" title="${button.title}" data-value="value" href="${button.href}" ${target}><i class="${button.icon}"></i></a>
  % else:
  <a class="${button.css_class}" data-toggle="tooltip" title="${button.title}" data-value="value" href="${button.href}" ${target}>${button.title}</a>
  % endif
  % endfor
</div>

