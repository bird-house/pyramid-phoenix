<div class="btn-group btn-group-vertical">
  % if len(buttongroup) > 0:
  % for name,value,icon,title,href in buttongroup:
  <a class="btn ${name}" data-value="${value}" href="${href}"><i class="${icon}"></i> ${title}</a>
  % endfor
  % endif
</div>

