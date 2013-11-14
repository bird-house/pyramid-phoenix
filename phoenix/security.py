ADMIN_USERS = ['carsten@linacs.org', 'nils.hempelmann@hzg.de', 'kipp@dkrz.de']

def groupfinder(userid, request):
    if userid in ADMIN_USERS:
        return ['group:admin']
    else:
        return ['group:editor']
