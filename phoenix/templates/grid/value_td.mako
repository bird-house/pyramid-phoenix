<div>
  <div>
    % for datum in data:
    %   if str(datum).startswith('file://'):
    <a class="label label-info" href="${datum}" target="_blank">URL</a>
    %   else:
    <span class="label label-default">${datum}</span>
    %   endif
    % endfor
  </div>
  % if format != None:
  <div>
    <a class="label label-info" href="${source}" target="_blank">${format}</a>
  </div>
  % endif
</div> 
