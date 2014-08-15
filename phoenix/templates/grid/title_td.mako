<div>
  <div>
    <b>${title}</b>
    % if abstact != None:
    <div>${abstract}</div>
    % endif
  </div>
  <div>
    % for keyword in keywords:
    <a href="#" class="label label-info">${keyword}</a>
    % endfor
  </div>
  % if format != None:
  <div>
    <a class="label label-warning" href="${source}">${format}</a>
  </div>
  % endif
</div> 
