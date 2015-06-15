<%
   _class = "text-danger"
   if state < 20:
      _class = "text-warning"
   elif state == 20:
      _class = "text-success"
%>
<span class="${_class}">${statename}</span>
