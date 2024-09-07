from flask import Flask, render_template, request, redirect
import pymysql

db = pymysql.connect(host="localhost", user="root", passwd="1203asdf", db="free_board", charset="utf8")
cur = db.cursor() # mysql 접속


app = Flask(__name__)

@app.route('/') #게시글 전체 목록
def index():
    cur.execute("SELECT * from board")
    pydata_list = cur.fetchall()
    return render_template('index.html', data_list=pydata_list)

@app.route('/write') # 작성 페이지 이동
def write():
    return render_template('write.html')

@app.route('/write_action', methods=['POST']) #작성
def write_action():
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

    sql = "INSERT INTO board (num, title, writer, content) VALUES (%s, %s, %s, %s)"
    values = (last + 1,title, writer, content)
    cur.execute(sql, values)
    db.commit()

    return redirect('/')

@app.route('/content/<int:num>') # 내용 보기
def content(num):
    cur.execute("SELECT * from board")
    pydata_list = cur.fetchall()
    return render_template('content.html', data_list=pydata_list[num - 1])
    
@app.route('/content/<int:num>/delete_content') #삭제
def delete_content(num):
    cur.execute("DELETE FROM board WHERE num = %s",num)
    #db.commit()  ## 삭제
    
    cur.execute("SELECT * from board")
    tu_db = cur.fetchall()
    
    if len(tu_db) != 0: ##삭제 후 정렬
        cur.execute("SELECT * from board")
        tu_db = cur.fetchall()
        max = tu_db[-1][0]
        for i in range(num,max):
            cur.execute("UPDATE board SET num = %s WHERE num = %s", (i, i + 1))
            
        
    db.commit()
    return redirect('/')

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

@app.route('/content/<int:num>/update') #수정 페이지 이동
def update_page(num):
    cur.execute("SELECT * from board")
    pydata_list = cur.fetchall()
    return render_template('update.html', data_list=pydata_list[num - 1])

@app.route('/content/update_action', methods = ['POST']) #수정 중
def update_action():
    update_content = request.form.get('update_content','')
    num2 = request.form.get('num2')
    
    cur.execute("UPDATE board SET content = %s WHERE num = %s",(update_content,num2))
    db.commit()
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)