<div class="btn-group" role="group">
  % for button in buttons:
  <a class="${button.css_class}" data-toggle="tooltip" title="${button.title}" data-value="value" href="${button.href}"><i class="${button.icon}"></i></a>
  % endfor
</div>

