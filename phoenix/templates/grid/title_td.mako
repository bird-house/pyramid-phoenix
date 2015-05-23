<div>
  <div>
    <a class="btn btn-link btn-lg" role="button" href="${url}">${title}</a>
    % if abstact != None:
    <div>${abstract}</div>
    % endif
  </div>
  <div>
    % for keyword in keywords:
    <a href="#" class="label label-info">${keyword}</a>
    % endfor
  </div>
  <div>
    % for datum in data:
    %   if str(datum).startswith('file://'):
    <a class="label label-warning" href="${datum}" target="_blank">URL</a>
    %   else:
    <span class="label">${datum}</span>
    %   endif
    % endfor
  </div>
  % if format != None:
  <div>
    <a class="label label-warning" href="${source}" target="_blank">${format}</a>
  </div>
  % endif
</div> 
