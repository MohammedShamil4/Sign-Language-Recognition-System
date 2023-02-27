import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect

from sign.models import *


def main(request):
    return render(request, 'login.html')


def approve_p(request):
    b = Parent.objects.all()
    return render(request, 'approve_parents.html',  {'val': b})


def manage_p(request):
    ob = Staff.objects.all()
    return render(request, 'manage_staff.html', {'val': ob})


def tip(request):
    return render(request, 'view_tips.html')


def sm(request):
    return render(request, 'view_studymaterials.html')


def rt(request):
    return render(request, 'rating.html')


def ub(request):
    return render(request, 'block.html')


def manage_s(request):
    return render(request, 'manage_materials.html')


def adm(request):
    return render(request, 'admin_home.html')


def log(request):
    username = request.POST['textfield']
    password = request.POST['textfield2']
    ob = Login.objects.get(username=username, password=password)
    if ob is not None:
        if ob.type == "admin":
            return redirect('adm')
        elif ob.type == "staff":
            request.session['lid'] = ob.id
            print(request.session['lid'])
            return redirect('sth')
        else:
            return HttpResponse('parent')
    else:
        return HttpResponse('''<script>alert("login failed");window.location="/"</script>''')


def out(request):
    return render(request, 'login.html')


def st_reg(request):
    return render(request, 'staff_reg.html')


def reg_stf(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    address = request.POST['textfield2']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    phone_number = request.POST['textfield5']
    email = request.POST['textfield6']
    password = request.POST['textfield7']

    ob = Login()
    ob.username = email
    ob.password = password
    ob.type = 'staff'
    ob.save()

    iob = Staff()
    iob.st_id = ob
    iob.name = name
    iob.gender = gender
    iob.address = address
    iob.post = post
    iob.pin = pin
    iob.phone_number = phone_number
    iob.email = email
    iob.save()

    return HttpResponse('''<script>alert("success");window.location="manage_p"</script>''')


def update_st(request, id):
    ob = Staff.objects.get(id=id)
    request.session['sid'] = id
    return render(request, 'stf_up.html', {'val': ob})


def up_st(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    address = request.POST['textfield2']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    phone_number = request.POST['textfield5']

    iob = Staff.objects.get(id=request.session['sid'])
    iob.name = name
    iob.gender = gender
    iob.address = address
    iob.post = post
    iob.pin = pin
    iob.phone_number = phone_number
    iob.save()

    return HttpResponse('''<script>alert("success");window.location="/manage_p"</script>''')


def delete_st(request, id):
    iob = Staff.objects.get(st_id__id=id)
    iob.delete()
    ob = Login.objects.get(id=id)
    ob.delete()
    return HttpResponse('''<script>alert("deleted");window.location="/manage_p"</script>''')


def sth(request):
    return render(request, 'staff_home.html')


def reg_pt(request):
    return render(request, 'parent_reg.html')


def reg_p(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    dob = request.POST['textfield2']
    address = request.POST['textfield3']
    post = request.POST['textfield4']
    pin = request.POST['textfield5']
    phone_number = request.POST['textfield6']
    email = request.POST['textfield7']
    password = request.POST['textfield8']
    ob = Login()
    ob.username = email
    ob.password = password
    ob.type = 'pending'
    ob.save()

    iob = Parent()
    iob.name = name
    iob.gender = gender
    iob.dob = dob
    iob.address = address
    iob.post = post
    iob.pin = pin
    iob.phone_number = phone_number
    iob.email = email
    iob.pt_id = ob
    iob.save()

    return HttpResponse('''<script>alert("success");window.location="log"</script>''')


def apr(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'parent'
    ob.save()
    return HttpResponse('''<script>alert("approved");window.location="/approve_p"</script>''')


def rej_p(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'rejected'
    ob.save()
    return HttpResponse('''<script>alert("rejected");window.location="/approve_p"</script>''')


def vp(request):
    ob = Parent.objects.filter(pt_id__type='parent')
    return render(request, 'view_parents.html',  {'val': ob})


def mg_tp(request):
    ob = Tip.objects.filter(st_id__st_id__id=request.session['lid'])
    return render(request, 'manage_tip.html', {'val': ob})


def ad_t(request):
    return render(request, 'tip_add.html')


def tp(request):
    tips = request.POST['textfield']
    date = datetime.datetime.now()
    st_id = Staff.objects.get(st_id__id=request.session['lid'])

    ob = Tip()
    ob.st_id = st_id
    ob.tip = tips
    ob.date = date
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/mg_tp"</script>''')


def upload_s(request):
    return render(request, 'upload_materials.html')

