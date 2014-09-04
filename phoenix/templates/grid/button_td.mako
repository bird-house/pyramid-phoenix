<div class="btn-group btn-group-vertical">
  % if len(buttongroup) > 0:
  % for name,value,icon,title,href,new_window in buttongroup:
  <% target = 'target="_blank"' if new_window else '' %>
  <a class="btn ${name}" data-value="${value}" href="${href}" ${target}><i class="${icon}"></i> ${title}</a>
  % endfor
  % endif
</div>

