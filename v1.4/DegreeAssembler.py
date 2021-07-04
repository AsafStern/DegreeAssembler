# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 23:57:45 2021

@author: Asaf Stern
"""



import tkinter as tk
from tkinter import ttk



class Course:
    def __init__(self, **kwargs):
        self.id = kwargs.pop("_id")
        self.kdams = set(kwargs.pop("kdams"))
        self.follow = set([])
        self.nkz = kwargs.pop("nkz")
        self.name = kwargs.pop("name")
        self.taught_on = kwargs.pop("taught_on") #0 fall, 1 spring
        self.color = 0  # 0 white, 1 grey, 2 black
        self.semester = None
        
        
    def reset(self):
        self.color = 0
        self.semester = None
        
        
    def __repr__(self):
        return self.name
    
    
    
    
class Graph:
    def __init__(self):
        self.vertexes = {} # course_id : course object
        self.sorted = []
        
    def reset(self):
        for v in self.vertexes.values():
            v.reset()
        self.sorted = []
        
    def add(self,*args):
        for course in args:
            self.vertexes[course.id] = course
            
        
    def DFS(self,v):
        v.color = 1
        for kdam in v.kdams:
            c = self.vertexes[kdam] 
            c.follow.add(v.id)
            if c.color == 0:
                self.DFS(c)
        self.sorted.append(v)
            
            
    def topological_sort(self):
        for c in self.vertexes.values():
            if c.color == 0:
                self.DFS(c)
        return self.sorted
                
            
    def __repr__(self):
        self.topological_sort()
        return self.sorted.__repr__()
    
    
    
    
class Curriculum():
    def __init__(self,*args):
        self.graph = args[0]
        self.semesters = self.reset_semesters()
        self.starting_point = 0
        self.create()
        
        
    def reset_semesters(self):
        return [[] for i in range(12)]
        
    def reset(self):
        self.graph.reset()
        self.semesters = self.reset_semesters()
        
        
    def set_starting_point(self,last_semester = 0, courses_done = []):
#        self.reset()
#        self.starting_point = last_semester
#        for c_id in courses_done:
#            c = self.graph.vertexes[c_id]
#            c.semester = last_semester
#            self.semesters[self.starting_point-1].append(c)
#        self.create()
        self.reset()
        print(f"last simester = {last_semester}")
        self.starting_point = last_semester
        for i,seme in enumerate(courses_done):
            for c_id in seme:
                c = self.graph.vertexes[c_id]
                c.semester = last_semester + i+1 -(len(courses_done))
                self.semesters[i].append(c)
        self.create()
            
            
    def sum_nkz(self,semester):
        return sum([c.nkz for c in self.semesters[semester]])
        
    
    def create(self):
        sort = self.graph.topological_sort()
        for course in sort:
            if not course.semester: # if None didnt yet enter curriculum
                learn_on = self.starting_point
                for kdam in course.kdams:
                    learn_on = max(learn_on,self.graph.vertexes[kdam].semester)
                if course.taught_on != (learn_on)%2 and course.taught_on != 2:#checkin the course is being tought on the semester else next
                    learn_on += 1
#                course.semester = learn_on + 1
#                self.semesters[learn_on].append(course)
                next_poss = 1 if course.taught_on == 2 else 2
                while self.sum_nkz(learn_on)+course.nkz > 24:
                    learn_on += next_poss
                course.semester = learn_on + 1
                self.semesters[learn_on].append(course)
                
                    
                
                
                
    def __repr__(self):
#        print(self.semesters)
        ret = ""
        if self.starting_point != 0:
            ret += f"קורסים שהושלמו:\n{self.semesters[self.starting_point-1]}\n\n"
        ret += f"סמסטר\tנק''ז\t\tקורסים\n"
        for i in range(self.starting_point,len(self.semesters)):
            nkz_sum = sum(c.nkz for c in self.semesters[i])
            if nkz_sum != 0:
                ret += f' -{i+1}-\t {float(nkz_sum)}\t{self.semesters[i]}\n'
        return ret
    
    
 
    
    
    
class NodeLabel(tk.Label):
    Edges = {}
    
    @classmethod
    def update_static_dict(cls):
        print("\nupdated\n")
        for node in NodeLabel.Edges.values():
            node.follow=[]
            node.kdams =[]
            for _id in node.data.follow:
                if _id in NodeLabel.Edges.keys():
                    node.follow.append(NodeLabel.Edges[_id])
            for _id in node.data.kdams:
                if _id in NodeLabel.Edges.keys():
                    node.kdams.append(NodeLabel.Edges[_id])
                    
                    
                    
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.data = None
        self.kdams = []
        self.follow = []
        self.is_clicked = False
        self.is_dclicked = False
        self.is_on = False
        self.is_moving = False
        self.current_row = 0
        self.orig_row = 0
        self.bind_all()
        
        
    def bind_all(self):
        self.bind("<1>", self.on_click)
        self.bind("<Up>",self.move_up)
        self.bind("<Down>",self.move_down)
        self.bind("<Return>", self.press_enter)
#        self.bind("<3>", self.on_rclick)
        
    def leave_focus(self):
        self.is_clicked = False
        self.is_dclicked = False
        self.is_on = False
        self.is_moving = False
        
    def update_notifiactions(self):
        if self.data.taught_on != 2 and self.data.taught_on != (self.current_row+1)%2:
            self.master.master.notifications_label1.configure(text = (" "*22)+"\nthis course\nisn't being\ntought on\nthis semeter")
        else:
            self.master.master.notifications_label1.configure(text = " "*22)
        tot_nkz = self.data.nkz
        if len(self.master.master.rows_widgets[self.current_row-1]) > 0:
            tot_nkz += float(self.master.master.rows_widgets[self.current_row-1][0]["text"])
        print(tot_nkz)
        if tot_nkz > 24 and self.current_row != self.orig_row:
            self.master.master.notifications_label2.configure(text = (" "*22)+"\nCredits\nover 24")
        else:
            self.master.master.notifications_label2.configure(text = " "*22)
        
    def move_(self):
        self.grid_forget()
        self.grid(row = self.current_row, column = self.master.master.mcis)
        
    def move_up(self, event):
#        print("upward")
        if self.current_row > 1:
            self.current_row -= 1
            self.move_()
            self.update_notifiactions()
        
    def move_down(self, event):
#        print("downward")
        if self.current_row < self.master.master.semesters_num:
            self.current_row += 1
            self.move_()
            self.update_notifiactions()
        
    def press_enter(self, event):
        print("enter")
        self.master.focus()
        self.master.master.notifications_label1.configure(text = (" "*22))
        self.master.master.notifications_label2.configure(text = (" "*22))
        self.master.master.replace_lines(self.orig_row,self.current_row, self)
        self.orig_row = self.current_row
        self.data.semester = self.current_row
        self.leave_focus()
        
        
    def on_rclick(self, event):
        self.grid_forget()
        self.master.master.add_to_courses_aside(self)
#        self.master.master.replace_lines(self.orig_row,13,self)
    
    
    def on_dclick(self, event):
        print("dclick")
        if self.is_moving:
            return
        for node in NodeLabel.Edges.values():
            if node.is_moving:
                return
        self.move_()
        self.is_on = False
        self.on_sclick()
        self.is_moving = True
        self.focus()
        self.current_row = self.data.semester
        self.orig_row = self.data.semester
        self.grid_forget()
        self.grid(row = self.current_row, column = self.master.master.mcis)
        
        
    def on_sclick(self):
        print("sclick")
        if not self.is_on:
            for node in NodeLabel.Edges.values():
                node.configure(bg = "grey94")
                node.configure(relief = "flat")
                if node != self:
                    node.is_on = False
        if self.is_on:
            self.configure(relief = "flat")
            for f in self.follow:
                f.configure(bg = "grey94")
            for k in self.kdams:
                k.configure(bg = "grey94")
            self.is_on = False
            self.master.master.option_menu_select(None)
        else:
            self.configure(relief = "solid")
            for f in self.follow:
                f.configure(bg = "#00ff00")
            for k in self.kdams:
                k.configure(bg = "#ff0000")
            self.is_on = True
            
        
    def off_click(self):
        if not self.is_dclicked:
            self.on_sclick()
        self.is_clicked = False
        self.is_dclicked = False
        
    def on_click(self,event):
        if self.is_clicked:
            self.is_dclicked = True
            self.on_dclick(event)
            return
        else:
            self.is_clicked = True
            self.master.after(300, self.off_click)
            
        
    def set_data(self, course):
        self.data = course
        NodeLabel.Edges[course.id] = self
#        NodeLabel.update_static_dict()
        
    def __str__(self):
        return self.data.name
    
    def __repr__(self):
        return self.data.name
        
        
    
    
    
class CGUI(tk.Tk):
    def __init__(self,*args,**kwargs):
        self.cur = kwargs.pop("cur")
        super().__init__(*args,**kwargs)
        self.configure(highlightbackground="black", highlightthickness=1)
        self.title(" Degree Assembler")
        self.semesters_num = 10
        self.rows_widgets = [[] for i in range(self.semesters_num)]
        self.courses_aside_lst = []
        self.courses_aside_om = None
        self.main = tk.Frame(self)
        self.notifications = tk.Frame(self.main)
        self.notifications_label1 = None
        self.notifications_label2 = None
        self.notifications_label3 = None
        self.instructions = tk.Frame(self)
        self.semester_var = None
        self.mcis = 50 #max courses in simester
        self.init_instructions()
#        NodeLabel.update_static_dict()
#        print(NodeLabel.Edges)
        
    def init_instructions(self):
        self.main.grid_forget()
        self.notifications.grid_forget()
        instructions = """
        Instructions:

        In the following frame you will see our curriculum's course arrange.
        
        To see every course's blockers and blockees: 
        \t- just click on the course.
        
        If you wish to move a course to be done in a different semester: 
        \t- double-click on the course,  
        \t- move it with up&down arrows,
        \t- insert it with the Enter key.
        
        The program allows you to calculate another
        curriculum arranged from a certain semester.
        The algorithm does it for you.
        To use the fetcher correctly do the following:
        \t- In the bottom left corener you will see a bottum\t
        \t  "Build a curriculum from semester:" with the
        \t  option to choose a semester.
        \t  Choose a semeter such that from this semester you will
        \t  be continue your studies. 
        \t- For every course you consider as done, move it 
        \t  to a semester you already done with smaller then the chosen earlier.
        \t  (double-click, arrows, Enter key)
        \t- For every course you wish to see where it could
        \t  be inserted, move it to one of the later
        \t  on semesters which the algorithm will work on.
        The program will calculate the fastest way
        To graduate starting from the chosen semeter.
        
        \t\t\t\tTo continue, click anywhere on the text
        """
        self.instructions = tk.Label(self ,text = instructions, anchor = "nw", justify = "left")
        self.instructions.grid(row = 0, column = 0)
#        self.instructions.grid()
        self.instructions.bind("<1>", self.instructions_click)
        
    def instructions_click(self, event):
        self.instructions.grid_forget()
        self.init_left_frame()
        self.init_right_frame()
        
        
    def init_left_frame(self):
        self.main.grid(row = 0, column = 0)
        self.main.configure(highlightbackground="black", highlightthickness=1)
        semesters = "ABCDEFGHIJKLMNOP"
        tk.Label(self.main, text = "- Semester -", font = ("Ariel",10)).grid(row = 0, column = 0, pady = 2, padx = 10)
        tk.Label(self.main, text = " - Credits - ", font = ("Ariel",10)).grid(row = 0, column = 1, pady = 2, padx = 10)
        tk.Label(self.main, text = " - Courses - ", font = ("Ariel",10)).grid(row = 0, column = 2, pady = 2, padx = 10, columnspan = self.mcis-2)
        tk.Label(self.main, text = " - Moving Courses - ", font = ("Ariel",10)).grid(row = 0, column = self.mcis)
#        instructions = """
#        Instructions:
#        To see each course's blocking and blocked courses, click on the course.
#        To move a course to different semester, double-cick the course and move with the up-down arrows,
#        press Enter to insert.
#        """
#        tk.Label(self.main, text = instructions, font = ("Ariel",10)).grid(row = 0, column = (self.mcis-8)//2, columnspan=self.mcis)
        for i in range(self.semesters_num):
            tex = f"_____  {semesters[i]}  _____"
            tk.Label(self.main, text = tex).grid(row = i+1, column = 0, pady = 2)
        self.update_all_lines()
            
            
    def update_all_lines(self, from_row = 0):
        for index,sim in enumerate(self.cur.semesters[from_row:]):
            index = index+from_row
#            print("in update_all_lines: ",index, sim)
            if len(sim) == 0:
                continue
            nkz_sum = sum(c.nkz for c in sim)
            l = tk.Label(self.main, text = f"{nkz_sum}")
            l.grid(row = index+1, column =1)
            self.rows_widgets[index].append(l)
            start_index = (self.mcis-len(sim))//2
            end_index = self.mcis - start_index if len(sim)%2==0 else self.mcis - start_index - 1
            in_sim_count = 0
            for i in range(start_index, end_index):
                lab = NodeLabel(self.main)
                lab.grid(row = index+1, column = i, padx = 10)
                d = sim[in_sim_count]
                in_sim_count += 1
                lab.set_data(d)
                lab["text"] = f"  {d.name}  "
                self.rows_widgets[index].append(lab)
            NodeLabel.update_static_dict()
#            nkz_sum = sum(c.nkz for c in sim)
#            tk.Label(self.main, text = f"{nkz_sum}").grid(row = index+1, column =1)
            
    def arrange_line(self,line_num):
        current = self.rows_widgets[line_num-1]
#        current.append(widget)
        current = current[1:]
        start_ind = (self.mcis-len(current))//2
        end_ind = self.mcis-start_ind if len(current)%2 == 0 else self.mcis - start_ind - 1
        count_nkz = 0
        for i in range(start_ind, end_ind):
            w = current[i-start_ind]
#            print(w.data)
            w.grid_forget()
            w.grid(row = line_num, column = i)
            count_nkz += w.data.nkz
        self.rows_widgets[line_num-1][0]["text"] = f"{count_nkz}"
            
        
    def replace_lines(self,old_line,new_line,widget):
#        print(old_line, new_line)
#        print(self.cur.semesters[old_line-1],self.cur.semesters[new_line-1])
        self.cur.semesters[old_line-1].remove(widget.data)
        self.cur.semesters[new_line-1].append(widget.data)
#        print(self.cur.semesters[old_line-1],self.cur.semesters[new_line-1])
        widget.grid_forget()
        self.rows_widgets[old_line-1].remove(widget)
        current = self.rows_widgets[new_line-1]
        current.append(widget)
        self.arrange_line(new_line)
        self.arrange_line(old_line)
        self.option_menu_select(None)
        
    
        
    def re_calculate(self, from_sim):
        for row in self.rows_widgets:
            for w in row[1:]:
                if w.is_moving:
                    w.focus()
                    print("a course is on the move")
                    self.notifications_label3.configure(text = "a course\nis still\nmoving")
                    self.after(4000, lambda : self.notifications_label3.configure(text = " "))
                    return
        print("recalculating")
        from_sim = "A B C D E F G H I J K L".split(" ").index(from_sim)
#        print(from_sim)
        consider_done = [[] for i in range(from_sim)]
        print(f"consider_done: {consider_done}")
        for i,s in enumerate(self.cur.semesters[:from_sim]):
            for c in s:
                consider_done[i].append(c.id)
#        print(f"consider done: {consider_done}")
        for i, rw in enumerate(self.rows_widgets[from_sim:]):
#            print(f"rw[1:] - {[w.data for w in rw[1:]]}")
            i += from_sim
            for w in rw:
                w.grid_forget()
#            print(f"some calc: {i}, {self.row_widgets.index(rw)}")
            self.rows_widgets[i] = []
        self.cur.semesters[-1] = [l.data for l in self.courses_aside_lst]
        self.cur.set_starting_point(from_sim,consider_done)
#        print(f"after recalculate: {self.cur.semesters}")
        self.update_all_lines(from_sim)
        print(f"self.cur.semeters:\n{self.cur.semesters}\n\nself.row_widgets:\n{self.rows_widgets}")
                    
       
    def option_menu_select(self,event):
        print("change selection to",self.semester_var.get())
        index = "A B C D E F G H I J K L M N O P".split(" ").index(self.semester_var.get())
        for rw in self.rows_widgets:
            for w in rw:
                w.configure(bg = "grey94")
        for rw in self.rows_widgets[:index]:
            for w in rw:
                w.configure(bg = "grey88")
        
        
    def add_to_courses_aside(self,course):
        self.courses_aside_lst.append(course)
#        print(self.courses_aside_lst)
        self.courses_aside_om = ttk.OptionMenu(self.notifications,tk.StringVar(),*self.courses_aside_lst)
        self.courses_aside_om.grid(row = 4, column = 1)
    
    def init_right_frame(self):
        self.notifications.grid(row = 15 , column = 0)
#        self.notifications.configure(highlightbackground="black", highlightthickness=1)
        options = " A B C D E F G H I J K L M N O P".split(" ")[:self.semesters_num+1]
        self.semester_var = tk.StringVar(self.notifications)
        self.semester_var.set("A")
        tk.Label(self.notifications, text = "Build from semester:", font = ("Ariel",10)).grid(row = 1, column = 0)
        ttk.OptionMenu(self.notifications, self.semester_var, *options, command = self.option_menu_select).grid(row = 2, column = 0)
        ttk.Button(self.notifications, text = "Build",command = lambda:self.re_calculate(self.semester_var.get())).grid(row = 3 ,column = 0)
        
        ttk.Button(self.main, text = "Instructions", command = self.init_instructions).grid(row = 15, column = self.mcis, sticky = "s")
        self.notifications_label1 = tk.Label(self.main,text =" "*22, fg = "#ff0000")
        self.notifications_label2 = tk.Label(self.main,text =" "*22, fg = "#5000dd")
        self.notifications_label3 = tk.Label(self.main,text =" "*22, fg = "#000000")
        self.notifications_label1.grid(row = 1, column = self.mcis+1, rowspan = 4)
        self.notifications_label2.grid(row = 5, column = self.mcis+1, rowspan = 4)
        self.notifications_label3.grid(row = 15, column = 1, rowspan = 4, columnspan = self.mcis, sticky = "w")   
            
            
            
            
            
            
if __name__=="__main__":   
    l = []
    
    l.append(Course(_id = "202-1-0011", kdams = [], nkz = 0, name = "בקיאות במתמ", taught_on = 0))
    l.append(Course(_id = "201-1-0201", kdams = [], nkz = 5, name = "לוגיקה", taught_on = 0))
    l.append(Course(_id = "201-1-9531", kdams = [], nkz = 4.5, name = "ליניארית", taught_on = 0))
    l.append(Course(_id = "202-1-0021", kdams = [], nkz = 1, name = "יישומים מתמטיים", taught_on = 0))
    l.append(Course(_id = "202-1-1011", kdams = [], nkz = 5, name = "מבוא למדמח", taught_on = 0))
    l.append(Course(_id = "382-1-1101", kdams = [], nkz = 3.5, name = "מבוא לנתונים", taught_on = 0))
    
    l.append(Course(_id = "201-1-2361", kdams = ["201-1-0201"], nkz = 5, name = "חדוא1", taught_on = 1))
    l.append(Course(_id = "202-1-1061", kdams = ["201-1-0201"], nkz = 5, name = "קומבי", taught_on = 1))
    l.append(Course(_id = "202-1-5181", kdams = ["202-1-1011"], nkz = 3, name = "OOP", taught_on = 1))
    l.append(Course(_id = "202-1-1031", kdams = ["202-1-1011"], nkz = 5, name = "מבני", taught_on = 1))
    l.append(Course(_id = "372-1-1105", kdams = ["202-1-1011"], nkz = 4, name = "מבוא לתוכנה", taught_on = 1))
    
    l.append(Course(_id = "372-1-3305", kdams = ["202-1-1031"], nkz = 3.5, name = "בסיסי", taught_on = 0))
    l.append(Course(_id = "202-1-2041", kdams = ["202-1-1031","202-1-1061","202-1-0021","201-1-9531"], nkz = 5, name = "אלגו", taught_on = 0))
    l.append(Course(_id = "202-1-2031", kdams = ["202-1-1031"], nkz = 5, name = "SPL", taught_on = 0))
    l.append(Course(_id = "201-1-2371", kdams = ["201-1-2361","202-1-1061"], nkz = 5, name = "חדוא2", taught_on = 0))
    l.append(Course(_id = "372-1-2501", kdams = ["201-1-0201","202-1-1031"], nkz = 3.5, name = "ECS", taught_on = 0))
    
    l.append(Course(_id = "202-1-2051", kdams = ["202-1-1031","202-1-2031","202-1-2041"], nkz = 5, name = "עקרונות שפות תכנות", taught_on =1))
    l.append(Course(_id = "201-1-2381", kdams = ["201-1-2371","202-1-1061"], nkz = 2.5, name = "הסתברות", taught_on = 1))
    l.append(Course(_id = "372-1-3401", kdams = ["372-1-1105","202-1-2031"], nkz = 5, name = "ניתוצ", taught_on = 1))    # mistake? software intro "372-1-1105"
#    l.append(Course(_id = "372-1-3401", kdams = ["202-1-2031"], nkz = 5, name = "ניתוצ", taught_on = 1))    # mistake? software intro "372-1-1105"
    
    l.append(Course(_id = "203-1-1371", kdams = ["201-1-9531","201-1-2371"], nkz = 3.5, name = "פיסיקה", taught_on = 1))
    l.append(Course(_id = "202-1-2011", kdams = ["201-1-0201","202-1-1061","202-1-2041"], nkz = 5, name = "מודלים חישוביים", taught_on = 1))
    
    l.append(Course(_id = "202-1-3021", kdams = ["202-1-2051","202-1-2011"], nkz = 5, name = "קומפי", taught_on = 0))   #requiered parallel "202-1-2081"
    l.append(Course(_id = "372-1-3041", kdams = ["372-1-2501","201-1-2381"], nkz = 3.5, name = "תקשורת נתונים", taught_on = 0))
    l.append(Course(_id = "202-1-2081", kdams = ["202-1-2031","372-1-2501"], nkz = 2, name = "מעבדה בSPL", taught_on = 0))
    l.append(Course(_id = "372-1-3071", kdams = ["201-1-2381"], nkz = 3.5, name = "סטטיסטיקה", taught_on = 0))
    l.append(Course(_id = "202-1-3051", kdams = ["372-1-3401","202-1-2031"], nkz = 3.5, name = "יסודות", taught_on = 0))
    
    l.append(Course(_id = "elective1", kdams = ["202-1-2011","202-1-2041"], nkz = 4, name = "בחירה", taught_on = 0))
    
    l.append(Course(_id = "202-1-3031", kdams = ["202-1-2031","202-1-2081"], nkz = 5, name = "מערכות הפעלה", taught_on = 1))
    l.append(Course(_id = "202-1-3061", kdams = ["201-1-0201","202-1-2011"], nkz = 5, name = "אימות תוכנה", taught_on = 1))
    l.append(Course(_id = "202-1-5141", kdams = ["372-1-3401","202-1-3051"], nkz = 3, name = "סדנא ליישום פרויקט", taught_on = 1))
    l.append(Course(_id = "372-1-4601", kdams = ["372-1-3305","372-1-3041"], nkz = 3.5, name = "אבטחת מחשבים ור", taught_on = 1))
    
    l.append(Course(_id = "373-1-4401", kdams = ["372-1-4601","202-1-5141"], nkz = 4, name = "פרוייקט 1", taught_on = 0))
    l.append(Course(_id = "372-1-3501", kdams = ["202-1-2031","372-1-3401"], nkz = 3.5, name = "הנדסת QA", taught_on = 0))
    l.append(Course(_id = "382-1-2705", kdams = ["201-1-2371","201-1-9531","202-1-2041"], nkz = 3.5, name = "אנליזה נומר", taught_on = 0))

    l.append(Course(_id = "373-1-4402", kdams = ["373-1-4401"], nkz = 5, name = "פרוייקט 2", taught_on = 1))
    g = Graph()
    g.add(*l)
    
    c = Curriculum(g)
#    c.create()
#    print("-תוכנית מקורית-")
#    print(c,"\n\n-תוכנית שלנו-")
#    
#    c.set_starting_point(3,["202-1-0011","201-1-0201","201-1-9531","202-1-0021",
#                            "202-1-1011","382-1-1101","201-1-2361","202-1-5181",
#                            "202-1-1031","372-1-3305","202-1-2031","201-1-2371",
#                            "372-1-2501","203-1-1371"])
#    print(c)
    
    #f_sim,f_index,to_sim = (int(i) for i in input("make a move: ").split(" "))
    #print(f_sim,f_index,to_sim, type(f_sim))
    
#    
    c = CGUI(cur = c)
    c.mainloop()