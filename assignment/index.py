from flask import Flask, render_template, request, redirect,session,url_for, send_file
import pymysql
import os
from werkzeug.utils import secure_filename


db = pymysql.connect(host="localhost", user="root", passwd="1203asdf", db="free_board", charset="utf8")
cur = db.cursor() # mysql 접속


app = Flask(__name__)
app.secret_key = "ABCDEFG"

@app.route('/', methods = ['POST' , 'GET']) #로그인 
def log():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        sql = "SELECT id FROM user WHERE id = %s AND pw = %s"
        value = (id, pw)
        cur.execute(sql, value)

        data = cur.fetchall()

        for row in data:
            data = row[0]
        
        if data:
            session['login_user'] = id
            return redirect('/board')
    
    
    return render_template('login.html')
    
@app.route('/register', methods=[ 'POST' , 'GET'])
def register():
    if request.method == 'POST':
        id = request.form['regi_id']
        pw = request.form['regi_pw']
        name = request.form['regi_name']
        birth = request.form['regi_birth']

        sql = "INSERT INTO user (id, pw, name, birth) VALUES (%s, %s, %s, %s)"
        value = (id, pw, name, birth)

        
        cur.execute(sql, value)
        db.commit()  
        return redirect('/')
        
    return render_template('register.html')
        
@app.route('/find_idpw', methods=[ 'POST' , 'GET']) #아이디 비번
def find_idpw():
    if request.method == 'POST':
        name = request.form['regi_name']
        birth = request.form['regi_birth']
        
        cur.execute("SELECT * from user where name = %s and birth = %s",(name, birth))
        list = cur.fetchone()
        return f"아이디 : {list[0]} , 비밀번호 : {list[1]}"
    return render_template('find_idpw.html')
    

@app.route('/board') #게시글 전체 목록
def index():
    cur.execute("SELECT * from board")
    pydata_list = cur.fetchall()
    return render_template('index.html', data_list=pydata_list)

@app.route('/my_profile', methods = ['POST','GET']) # 내 프로필
def myprofile():
    id = session['login_user']
    cur.execute("SELECT * from user where id = %s",id)
    my_profile = cur.fetchone()
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        profile_image = request.files.get('profile_image')
        
        if profile_image:
            filename = secure_filename(profile_image.filename) 
            profile_image.save('./static/images/' + filename)
    
            cur.execute("UPDATE user SET image = %s WHERE id = %s", (filename, id))   
        
        cur.execute("UPDATE user SET name = %s WHERE id = %s",( name ,id))
        cur.execute("UPDATE board SET writer = %s WHERE id = %s",( name ,id))
        db.commit()
        
        cur.execute("SELECT * from user where id = %s",id)
        my_profile = cur.fetchone()
        
        return render_template('myprofile.html', data_list= my_profile)
    
    return render_template('myprofile.html', data_list= my_profile)
    
@app.route('/profile/<writer>/', methods=['GET']) # 상대 프로필
def profile(writer):
    
    cur.execute("SELECT * from user where name = %s",writer)
    profile = cur.fetchone()
    
    return render_template('profile.html', data_list= profile)
    


@app.route('/write', methods=[ 'POST' , 'GET']) # 작성 
def write():
    if request.method == 'POST':
        cur.execute("SELECT * from board")
        tu_db = cur.fetchall()
    
        if len(tu_db) == 0:
            last = 0
        else:
            cur.execute("SELECT MAX(num) from board")
            tu_db = cur.fetchall()
            last = tu_db[0][0]
        
        title = request.form.get('title')
        writer = request.form.get('writer')
        content = request.form.get('content')
        public = request.form.get('public')
        if public == '비공개':
            password = request.form.get('password')
        else:
            password = None
        id = session['login_user']
        
        file = request.files.get('file')
     
        if file:
            filename = secure_filename(file.filename) 
            file.save('./static/files/' + filename)
    
            cur.execute("UPDATE board SET filename = %s WHERE id = %s", (filename, id))
        
        
        
        sql = "INSERT INTO board (num, title, writer, content, public, password, id) VALUES (%s, %s, %s, %s, %s,%s, %s)"
        values = (last + 1,title, writer, content, public, password,id)
        cur.execute(sql, values)
        db.commit()

        return redirect('/board')
        
    ###
    id = session['login_user']
    cur.execute("SELECT * from user where id = %s",id)
    data = cur.fetchall()
    name = data[0][2]
    return render_template('write.html',name = name)

@app.route('/download/<int:num>', methods=['GET']) #파일 다운로드
def download(num):
    
    sql = "SELECT filename FROM board WHERE num = %s"
    cur.execute(sql, num)
    file_data = cur.fetchone()

    if file_data[0]:
        filename = file_data[0]
        file_path = os.path.join('./static/files/', filename)
        
        return send_file(file_path, as_attachment=True)
        
    return "다운로드할 파일이 없습니다."

@app.route('/content/<int:num>', methods=['GET', 'POST'])  # 내용 보기
def content(num):
    cur.execute("SELECT * from board WHERE num = %s", (num,))
    data = cur.fetchone()
    
    if request.method == 'POST':
        input_password = request.form.get('password')
        if data[5] == input_password:  # 비밀번호 확인
            return render_template('content.html', data_list=data)
        else:
            return "비밀번호가 틀렸습니다. 다시 시도하세요."

    # 비공개일 경우 입력란으로 이동
    if data[4] == '비공개':
        return render_template('password_input.html', num=num)
    
    # 공개일 경우
    return render_template('content.html', data_list=data)





@app.route('/content/<int:num>/delete_content') #삭제
def delete_content(num):
    cur.execute("DELETE FROM board WHERE num = %s",num)
    db.commit()  ## 삭제
    
    cur.execute("SELECT * from board")
    tu_db = cur.fetchall()
    
    if len(tu_db) != 0: ##삭제 후 정렬
        cur.execute("SELECT * from board")
        tu_db = cur.fetchall()
        max = tu_db[-1][0]
        for i in range(num,max):
            cur.execute("UPDATE board SET num = %s WHERE num = %s", (i, i + 1))
            
        
    db.commit()
    return redirect('/board')

@app.route('/find') # 검색 페이지로 이동
def find_page():
    return render_template('find.html')

@app.route('/find_action1', methods = ['POST']) # 검색  case1
def finding1():
    
    title_find = request.form.get('title_find', '')
    
    
    if title_find != '':
        cur.execute("SELECT * FROM board WHERE title LIKE %s", ('%'+ title_find +'%'))
        pytitle_list = cur.fetchall()  
        
        return render_template('find.html',title_list = pytitle_list)  
    else:
        cur.execute("SELECT * FROM board WHERE title LIKE %s", title_find)
        pytitle_list = cur.fetchall()  
        
        return render_template('find.html',title_list = pytitle_list)  
    
    
@app.route('/find_action2', methods = ['POST']) # 검색 중 case2
def finding2():
    content_find = request.form.get('content_find', '')
    
    if content_find != '':
        cur.execute("SELECT * FROM board WHERE content LIKE %s", ('%'+ content_find +'%'))
        pycontent_list = cur.fetchall()  
        
        return render_template('find.html',content_list = pycontent_list)  
    else:
        cur.execute("SELECT * FROM board WHERE content LIKE %s", content_find)
        pycontent_list = cur.fetchall()  
        
        return render_template('find.html',content_list = pycontent_list) 

@app.route('/find_action3', methods = ['POST']) # 검색 중 case3
def finding3():
    all_find = request.form.get('all_find', '')
    
    if all_find != '':
        cur.execute("SELECT * FROM board WHERE title LIKE %s OR content LIKE %s", ('%'+ all_find +'%','%'+ all_find +'%'))
        pyall_list = cur.fetchall()  
        
        return render_template('find.html',all_list = pyall_list)  
    else:
        cur.execute("SELECT * FROM board WHERE title LIKE %s OR content LIKE %s", (all_find,all_find))
        pyall_list = cur.fetchall()  
        
        return render_template('find.html',all_list = pyall_list) 

@app.route('/content/<int:num>/update',methods = ['POST','GET']) #수정 
def update_page(num):
    log_id = session['login_user']
    cur.execute("SELECT id FROM board WHERE num = %s",num)
    writer_id = cur.fetchone() 
    
    if log_id == writer_id[0]:
        if request.method == 'POST':
            update_content = request.form['update_content']
    
            cur.execute("UPDATE board SET content = %s WHERE num = %s",(update_content,num))
            db.commit()
    
            return redirect('/board')
    else:
        return "자신이 작성한 글만 수정할 수 있습니다. "
        
    
    cur.execute("SELECT * from board WHERE num = %s", (num))
    pydata_list = cur.fetchone() 
    
    return render_template('update.html', data_list=pydata_list)


if __name__ == '__main__':
    app.run(debug=True)