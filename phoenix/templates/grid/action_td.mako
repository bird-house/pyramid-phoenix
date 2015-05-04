<div class="btn-group" role="group">
  % if len(buttongroup) > 0:
  % for name,value,icon,title,href,new_window in buttongroup:
  <% target = 'target="_blank"' if new_window else '' %>
  <a class="btn btn-default ${name}" data-value="${value}" href="${href}" ${target}><i class="${icon}"></i></a>
  % endfor
  % endif
</div>

