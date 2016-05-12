<div class="btn-group" role="group">
  % for button in buttons:
  <% target = 'target="_blank"' if button.new_window else '' %>       
  <a class="${button.css_class}" data-toggle="tooltip" title="${button.title}" data-value="value" href="${button.href}" ${target}><i class="${button.icon}"></i></a>
  % endfor
</div>

