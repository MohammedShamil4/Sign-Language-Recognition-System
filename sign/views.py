from datetime import datetime

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from sign.models import *

import cv2
# login page


def main(request):
    return render(request, 'index.html')


def logins(request):
    return render(request, 'login.html')


@login_required(login_url='/')
def approve_p(request):
    b = Parent.objects.all().order_by('id').reverse()
    return render(request, 'approve_parents.html',  {'val': b})


@login_required(login_url='/')
def manage_p(request):
    ob = Staff.objects.all()
    return render(request, 'manage_staff.html', {'val': ob})


@login_required(login_url='/')
def tip(request):
    ob = Tip.objects.all().order_by('id').reverse()
    return render(request, 'view_tips.html', {'val': ob})


@login_required(login_url='/')
def sm(request):
    return render(request, 'view_studymaterials.html')


@login_required(login_url='/')
def stm(request):
    types = request.POST['select']
    ob = Study.objects.filter(classes=types)
    print(ob)
    return render(request, 'view_studymaterials.html', {'val': ob,'s':types})


@login_required(login_url='/')
def rt(request):
    ob = Staff.objects.all()
    return render(request, 'rating.html', {'val': ob})


@login_required(login_url='/')
def ub(request):
    return render(request, 'block.html')


@login_required(login_url='/')
def ubs(request):

    types = request.POST['select']
    if types == 'parent':
        ob = Parent.objects.all()
        return render(request, 'block.html', {'val': ob, 's': types})
    else:
        ob=Staff.objects.all()
        return render(request, 'block.html', {'val': ob, 's': types})


def block_parent(request,id):

    ob = Login.objects.get(id=id)
    ob.type = 'blocked'
    ob.save()
    return HttpResponse('''<script>alert("successfully blocked");window.location="/ub"</script>''')


def block_staff(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'blocked'
    ob.save()
    return HttpResponse('''<script>alert("successfully blocked");window.location="/ub"</script>''')


def unblock_parent(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'parent'
    ob.save()
    return HttpResponse('''<script>alert("successfully unblocked");window.location="/ub"</script>''')


def unblock_staff(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'staff'
    ob.save()
    return HttpResponse('''<script>alert("successfully unblocked");window.location="/ub"</script>''')


@login_required(login_url='/')
def manage_s(request):
    ob = Study.objects.filter(st_id__st_id__id=request.session['lid'])
    return render(request, 'manage_materials.html', {'val': ob})


@login_required(login_url='/')
def adm(request):
    return render(request, 'admin_home.html')


def log(request):
    username = request.POST['textfield']
    password = request.POST['textfield2']
    try:
        ob = Login.objects.get(username=username, password=password)
        check_user = ob.username == username
        check_password = ob.password == password
        if ob and check_user and check_password:
            if ob.type == "admin":
                ob1 = auth.authenticate(username='admin', password='admin')
                auth.login(request, ob1)
                return redirect('adm')
            elif ob.type == "staff":
                ob1 = auth.authenticate(username='admin', password='admin')
                auth.login(request, ob1)
                request.session['lid'] = ob.id
                print(request.session['lid'])
                return redirect('sth')
            elif ob.type == "parent":
                ob1 = auth.authenticate(username='admin', password='admin')
                auth.login(request, ob1)
                request.session['lid'] = ob.id
                print(request.session['lid'])
                return redirect('pt_hm')

        else:
            return HttpResponse('''<script>alert("login failed");window.location="/"</script>''')
    except:
        return HttpResponse('''<script>alert("login failed");window.location="/"</script>''')


@login_required(login_url='/')
def out(request):
    return render(request, 'login.html')


@login_required(login_url='/')
def st_reg(request):
    return render(request, 'staff_reg.html')


@login_required(login_url='/')
def reg_stf(request):
    try:
        name = request.POST['textfield']
        gender = request.POST['radiobutton']
        address = request.POST['textfield2']
        post = request.POST['textfield3']
        pin = request.POST['textfield4']
        phone_number = request.POST['textfield5']
        email = request.POST['textfield6']
        password = request.POST['textfield7']
        qualification = request.POST['textfield10']
        image = request.FILES['file']
        fs = FileSystemStorage()
        fp = fs.save(image.name, image)

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
        iob.image = image
        iob.qualification = qualification
        iob.post = post
        iob.pin = pin
        iob.phone_number = phone_number
        iob.email = email
        iob.save()

        return HttpResponse('''<script>alert("success");window.location="/manage_p"</script>''')

    except:
        return HttpResponse('''<script>alert("email already exists");window.location="/st_reg"</script>''')


@login_required(login_url='/')
def update_st(request, id):
    ob = Staff.objects.get(id=id)
    request.session['sid'] = id
    return render(request, 'stf_up.html', {'val': ob})


@login_required(login_url='/')
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


@login_required(login_url='/')
def delete_st(request, id):
    iob = Staff.objects.get(st_id__id=id)
    iob.delete()
    ob = Login.objects.get(id=id)
    ob.delete()
    return HttpResponse('''<script>alert("deleted");window.location="/manage_p"</script>''')


@login_required(login_url='/')
def sth(request):
    return render(request, 'staff_home.html')


def reg_pt(request):
    return render(request, 'parent_reg.html')


def reg_p(request):
    try:
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
        request.session['pid']=iob.id

        return HttpResponse('''<script>alert("success");window.location="/std_reg"</script>''')
    except:
        return HttpResponse('''<script>alert("email already exists");window.location="/reg_pt"</script>''')


@login_required(login_url='/')
def apr(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'parent'
    ob.save()
    return HttpResponse('''<script>alert("approved");window.location="/approve_p"</script>''')


@login_required(login_url='/')
def rej_p(request, id):
    ob = Login.objects.get(id=id)
    ob.type = 'rejected'
    ob.save()
    return HttpResponse('''<script>alert("rejected");window.location="/approve_p"</script>''')


@login_required(login_url='/')
def vp(request):
    ob = Parent.objects.filter(pt_id__type='parent').order_by('id').reverse()
    return render(request, 'view_parents.html',  {'val': ob})


@login_required(login_url='/')
def mg_tp(request):
    ob = Tip.objects.filter(st_id__st_id__id=request.session['lid'])
    return render(request, 'manage_tip.html', {'val': ob})


@login_required(login_url='/')
def ad_t(request):
    return render(request, 'tip_add.html')


@login_required(login_url='/')
def tp(request):
    tips = request.POST['textfield']
    date = datetime.today()
    st_id = Staff.objects.get(st_id__id=request.session['lid'])

    ob = Tip()
    ob.st_id = st_id
    ob.tip = tips
    ob.date = date
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/mg_tp"</script>''')


@login_required(login_url='/')
def upload_s(request):
    return render(request, 'upload_materials.html')


@login_required(login_url='/')
def up_s(request):
    materials = request.FILES['file']
    fs = FileSystemStorage()
    fp = fs.save(materials.name, materials)

    description = request.POST['textfield']
    division = request.POST['textfield2']
    subject = request.POST['textfield3']

    ob = Study()
    ob.materials = fp
    ob.date = datetime.today()
    ob.description = description
    ob.st_id = Staff.objects.get(st_id__id=request.session['lid'])
    ob.classes = division
    ob.subject = subject
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/manage_s"</script>''')


@login_required(login_url='/')
def pt_hm(request):
    return render(request, 'parent_home.html')


@login_required(login_url='/')
def ad_sm(request):
    return render(request, 'adminview_studymaterials.html')


@login_required(login_url='/')
def ad_stm(request):
    type = request.POST['select']
    ob = Study.objects.filter(classes=type)
    return render(request, 'adminview_studymaterials.html', {'val': ob, 's': type})


@login_required(login_url='/')
def mg_w(request):
    ob = Class.objects.filter(st_id__st_id__id=request.session['lid'])
    return render(request, 'manage_work.html', {'val': ob})


@login_required(login_url='/')
def up_w(request):
    return render(request, 'upload_work.html')


@login_required(login_url='/')
def st_c(request):
    ob = Parent.objects.filter(pt_id__type='parent')
    return render(request, 's_search.html', {'val': ob})


@login_required(login_url='/')
def st_cc(request, id):
    ob = Parent.objects.get(pt_id__id=id)
    request.session['sid'] = id
    from django.db.models import Q
    obb = Chat.objects.filter(Q(fromid=request.session['lid'], toid=request.session['sid']) | Q(fromid=request.session['sid'], toid=request.session['lid'])).order_by('id')
    return render(request, 'staff_chat.html', {'val': ob, 'data': obb, 'fr': request.session['lid']})


@login_required(login_url='/')
def chat_s(request):
    msg = request.POST['textarea']
    ob = Chat()
    ob.fromid = Login.objects.get(id=request.session['lid'])
    ob.toid = Login.objects.get(id=request.session['sid'])
    ob.date = datetime.today()
    ob.message = msg
    ob.save()
    return redirect('/red_c')


@login_required(login_url='/')
def red_c(request):
    ob = Parent.objects.get(pt_id__id=request.session['sid'])
    from django.db.models import Q
    obb = Chat.objects.filter(Q(fromid=request.session['lid'], toid=request.session['sid']) | Q(fromid=request.session['sid'], toid=request.session['lid'])).order_by('id')
    return render(request, 'staff_chat.html', {'val': ob, 'data': obb, 'fr': request.session['lid']})


@login_required(login_url='/')
def rmg(request):
    b = Staff.objects.all()
    return render(request, 'ratingmg.html', {'val': b})


@login_required(login_url='/')
def sr(request):
    staff = request.POST['select']
    ratings = request.POST['select2']
    review = request.POST['textfield']

    ob = Review()
    ob.st_id = Staff.objects.get(id=staff)
    ob.pt_id = Parent.objects.get(pt_id__id=request.session['lid'])
    ob.rating = ratings
    ob.review = review
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/rmg"</script>''')


@login_required(login_url='/')
def update_tp(request, id):
    ob = Tip.objects.get(id=id)
    request.session['sid'] = id
    return render(request, 'tip_up.html', {'val': ob})


@login_required(login_url='/')
def u_tp(request):
    tips = request.POST['textfield']

    ob = Tip.objects.get(id=request.session['sid'])
    ob.tip = tips
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/mg_tp"</script>''')


@login_required(login_url='/')
def delete_tip(request, id):
    iob = Tip.objects.get(id=id)
    iob.delete()
    return HttpResponse('''<script>alert("deleted");window.location="/mg_tp"</script>''')


@login_required(login_url='/')
def pc(request):
    ob = Staff.objects.all()
    return render(request, 'pt_chat.html',  {'val': ob})


@login_required(login_url='/')
def pt_cc(request, id):
    ob = Staff.objects.get(st_id__id=id)
    request.session['sid'] = id
    from django.db.models import Q
    obb = Chat.objects.filter(Q(fromid=request.session['lid'], toid=request.session['sid']) | Q(fromid=request.session['sid'], toid=request.session['lid'])).order_by('id')
    return render(request, 'parent_chat.html', {'val': ob, 'data': obb, 'fr': request.session['lid']})


@login_required(login_url='/')
def chat_p(request):
    msg = request.POST['textarea']
    ob = Chat()
    ob.fromid = Login.objects.get(id=request.session['lid'])
    ob.toid = Login.objects.get(id=request.session['sid'])
    ob.date = datetime.today()
    ob.message = msg
    ob.save()
    return redirect('/rd_c')


@login_required(login_url='/')
def rd_c(request):
    ob = Staff.objects.get(st_id__id=request.session['sid'])
    from django.db.models import Q
    obb = Chat.objects.filter(Q(fromid=request.session['lid'], toid=request.session['sid']) | Q(fromid=request.session['sid'], toid=request.session['lid'])).order_by('id')
    return render(request, 'parent_chat.html', {'val': ob, 'data': obb, 'fr': request.session['lid']})


@login_required(login_url='/')
def up_mts(request, id):
    ob = Study.objects.get(id=id)
    request.session['sid'] = id
    return render(request, 'update_materials.html', {'val': ob})


@login_required(login_url='/')
def up_ms(request):
    description = request.POST['textfield']
    division = request.POST['textfield2']
    subject = request.POST['textfield3']

    ob = Study.objects.get(id=request.session['sid'])
    ob.date = datetime.today()
    ob.description = description
    ob.classes = division
    ob.subject = subject
    ob.save()
    return HttpResponse('''<script>alert("updated");window.location="/manage_s"</script>''')


@login_required(login_url='/')
def dlt_study(request, id):
    iob = Study.objects.get(id=id)
    iob.delete()

    return HttpResponse('''<script>alert("deleted");window.location="/manage_s"</script>''')


@login_required(login_url='/')
def ad_tp(request):
    ob = Tip.objects.all().order_by('id').reverse()
    return render(request, 'admin_tips.html', {'val': ob})


def std_reg(request):
    return render(request, 'student_reg.html')


def insert_st(request):

    name = request.POST['name']
    admission = request.POST['adm']
    division = request.POST['select']

    ob = Student()
    ob.name = name
    ob.pt_id = Parent.objects.get(id=request.session['pid'])
    ob.admission_no = admission
    ob.division = division
    ob.save()

    return HttpResponse('''<script>alert("added");window.location="/std_reg"</script>''')


@login_required(login_url='/')
def pts_hm(request):
    ob = Parent.objects.filter(pt_id__id=request.session['lid'])
    return render(request, 'pthm.html', {'val': ob})


@login_required(login_url='/')
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url='/')
def sen_r(request):

    review = request.POST['review']
    rating = request.POST['star-rating']
    staff_id = request.POST['select']

    ob = Review()
    ob.review = review
    ob.rating = rating
    ob.pt_id = Parent.objects.get(pt_id__id=request.session['lid'])
    ob.st_id = Staff.objects.get(id=staff_id)
    ob.save()

    return HttpResponse('''<script>alert("added");window.location="/rt"</script>''')


@login_required(login_url='/')
def ad_vrg(request):
    ob = Review.objects.all()
    return render(request, 'adm_rting.html', {'val': ob})


@login_required(login_url='/')
def up_cw(request):
    materials = request.FILES['file']
    fs = FileSystemStorage()
    fp = fs.save(materials.name, materials)

    description = request.POST['textfield']
    division = request.POST['textfield2']
    subject = request.POST['textfield3']

    ob = Class()
    ob.work = fp
    ob.date = datetime.today()
    ob.description = description
    ob.st_id = Staff.objects.get(st_id__id=request.session['lid'])
    ob.classes = division
    ob.subject = subject
    ob.save()
    return HttpResponse('''<script>alert("upload");window.location="/mg_w"</script>''')


@login_required(login_url='/')
def update_cw(request, id):
    ob = Study.objects.get(id=id)
    request.session['sid'] = id
    return render(request, 'update_classwork.html', {'val': ob})


@login_required(login_url='/')
def updt_cw(request):
    description = request.POST['textfield']
    division = request.POST['textfield2']
    subject = request.POST['textfield3']

    ob = Class.objects.get(id=request.session['sid'])
    ob.date = datetime.today()
    ob.description = description
    ob.classes = division
    ob.subject = subject
    ob.save()
    return HttpResponse('''<script>alert("updated");window.location="/mg_w"</script>''')


@login_required(login_url='/')
def class_w(request):
    return render(request, 'view_classwork.html')


@login_required(login_url='/')
def class_wk(request):
    types = request.POST['select']
    ob = Class.objects.filter(classes=types)
    return render(request, 'view_classwork.html', {'val': ob, 's': types})


@login_required(login_url='/')
def dlt_work(request, id):
    iob = Class.objects.get(id=id)
    iob.delete()
    return HttpResponse('''<script>alert("deleted");window.location="/mg_w"</script>''')


@login_required(login_url='/')
def feeds(request):
    ob = Student.objects.all()
    return render(request, 'feed_bk.html', {'val': ob})


@login_required(login_url='/')
def s_feed(request,id):
    request.session['ptid'] = id
    return render(request, 'send_feed.html')


@login_required(login_url='/')
def s_fd(request):
    feedback = request.POST['textfield']

    ob = Feedback()
    ob.feedback = feedback
    ob.st_id = Staff.objects.get(st_id__id=request.session['lid'])
    ob.pt_id = Parent.objects.get(id=request.session['ptid'])
    ob.date = datetime.today()
    ob.save()
    return HttpResponse('''<script>alert("sended");window.location="/feeds"</script>''')


@login_required(login_url='/')
def v_fd(request):
    ob = Feedback.objects.filter(pt_id__pt_id__id=request.session['lid'])
    return render(request, 'view_feedback.html', {'val': ob})


@login_required(login_url='/')
def st_rev(request):
    ob = Review.objects.filter(st_id__st_id__id=request.session['lid'])
    return render(request, 'staff_review.html', {'val': ob})


def texts(request):
    return render(request, 'text.html')


# def ffplay():
#     gc1 = GestureController()
#     gc1.start()
#     gc1.stop()
#
#
# def gest(request):
#     gc1 = GestureController()
#     print("=========================")
#     # start_new_thread(ffplay, ())
#     gc1.start()
#     gc1.stop()
#     cap = cv2.VideoCapture(0)
#     cap.release()
#
#     cv2.destroyAllWindows()
#     return redirect('/')


def translate_text(request):
    from sampleeeeee import generate_video
    word = request.POST['textfield']

    txt1 = generate_video(word)

    return render(request, 'text.html',{"val":txt1})


