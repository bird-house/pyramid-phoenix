<div class="btn-group btn-group-vertical">
  % if len(buttongroup) > 0:
  % for name,value,icon,title in buttongroup:
  <button class="btn ${name}" data-value="${value}"><i class="${icon}"></i> ${title}</button>
  % endfor
  % endif
</div>

