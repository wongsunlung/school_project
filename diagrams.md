```
#結構圖
graph TB
    classDef project fill:#f9f0ff,stroke:#d3adf7,stroke-width:2px,color:#000;
    classDef coreClass fill:#e6f7ff,stroke:#91d5ff,stroke-width:2px,color:#000;
    classDef appClass fill:#f6ffed,stroke:#b7eb8f,stroke-width:2px,color:#000;
    classDef resClass fill:#fff7e6,stroke:#ffd591,stroke-width:2px,color:#000;

    subgraph Project_Root ["校務課表管理系統專案邊界 (school_demo2 Root)"]
        subgraph core ["⚙️ 專案大腦 (core Project)"]
            settings["settings.py<br>(全域配置中心)"]
            urls_core["urls.py<br>(第一分流總路由)"]
        end
        subgraph Apps ["🧩 業務應用層 (Applications)"]
            subgraph main_base ["main_base<br>(基礎入口 App)"]
                mb_index["網站入口控制"]
                mb_models["全網站 models.py<br>(數據庫主骨架)"]
                mb_admin["全網站 admin.py<br>(後台管理註冊)"]
            end
            subgraph office ["office<br>(教務管理子系統)"]
                off_1["班級模組"]
                off_2["課程模組"]
                off_3["學生管理"]
                off_4["老師管理"]
            end
            subgraph student ["student<br>(學生子系統)"]
                std_1["課表觀看模組"]
                std_2["成績查詢模組"]
                std_3["學生入口主頁"]
                std_4["選課模組"]
                std_5["個人資訊管理"]
            end
            subgraph teacher ["teacher<br>(教師子系統)"]
                tch_1["學生出席率管理"]
                tch_2["學生成績登錄"]
                tch_3["老師課表及入口"]
                tch_4["選課管理對應"]
                tch_5["個人資訊管理"]
            end
            subgraph user_app ["user<br>(用戶權限 App)"]
                usr_auth["用戶認證 / 權限校驗"]
            end
        end
        subgraph Resources ["🎨 前端視覺與靜態資源 (Assets & UI)"]
            subgraph templates ["templates/<br>(HTML 視圖網格)"]
                t_root["base.html<br>index.html"]
                t_off["office/<br>(4個 HTML 視圖)"]
                t_std["student/<br>(4個 HTML 視圖)"]
                t_tch["teacher/<br>(4個 HTML 視圖)"]
                t_usr["user/<br>(2個 HTML 視圖)"]
            end
            subgraph static ["static/<br>(靜態資源庫)"]
                s_css["css/ 資料夾<br>(admin.css, all.css,<br>bootstrap.css, lightbox.css)"]
                s_js["js/ 資料夾<br>(bootstrap.bundle, jquery,<br>lightbox, main.js)"]
            end
        end
    end

    urls_core --> main_base
    urls_core --> office
    urls_core --> student
    urls_core --> teacher
    urls_core --> user_app
    mb_models -.-> templates
    main_base ==> t_root
    office ==> t_off
    student ==> t_std
    teacher ==> t_tch
    user_app ==> t_usr
    templates -.-> static

    class Project_Root project;
    class core coreClass;
    class main_base,office,student,teacher,user_app appClass;
    class templates,static resClass;


#路由分流圖

graph LR
    classDef coreStyle fill:#edf4ff,stroke:#1890ff,stroke-width:2px,color:#000;
    classDef pathStyle fill:#fffbe6,stroke:#ffa940,stroke-width:2px,color:#000;
    classDef appStyle fill:#f6ffed,stroke:#52c41a,stroke-width:2px,color:#000;
    classDef viewStyle fill:#fff0f6,stroke:#eb2f96,stroke-width:2px,color:#000;
    classDef templateStyle fill:#f9f0ff,stroke:#722ed1,stroke-width:2px,color:#000;

    subgraph Root ["🌐 Core 第一分流總路由控制中心 (core/urls.py)"]
        CoreURL["HTTP 請求<br>URL 總解析器"]
    end

    CoreURL ==> |"path('admin/')"| AdminApp["🧱 內建超級管理員後台<br>(admin.site.urls)"]
    AdminApp --> AdminTarget["💻 直接存取後台<br>localhost/admin"]

    CoreURL ==> |"path(' ')"| Path2["🏠 main_base 全站首頁<br>namespace='main_base'"]
    subgraph Sub2 ["main_base 請求生命週期"]
        Path2 --> MB_URL["main_base/urls.py"] --> MB_View["views.py"] --> MB_Tpl["index.html"]
    end

    CoreURL ==> |"path('users/')"| Path3["🔐 用戶驗證與註冊模組<br>namespace='users'"]
    subgraph Sub3 ["users 請求生命週期"]
        Path3 --> US_URL["users/urls.py"] --> US_View["views.py"] --> US_Tpl["login.html<br>register.html<br>logout.html"]
    end

    CoreURL ==> |"path('office/')"| Path4["🏢 行政管理端模組<br>namespace='office'"]
    subgraph Sub4 ["office 請求生命週期"]
        Path4 --> OF_URL["office/urls.py"] --> OF_View["views.py"] --> OF_Tpl["office.html<br>admin_classrooms.html<br>admin_courses.html<br>admin_students.html<br>admin_teachers.html"]
    end

    CoreURL ==> |"path('teachers/')"| Path5["👨‍🏫 教師教學端模組<br>namespace='teachers'"]
    subgraph Sub5 ["teachers 請求生命週期"]
        Path5 --> TC_URL["teachers/urls.py"] --> TC_View["views.py"] --> TC_Tpl["teacher.html<br>attendance.html<br>grades.html<br>profile.html"]
    end

    CoreURL ==> |"path('students/')"| Path6["🎓 學生事務端模組<br>namespace='students'"]
    subgraph Sub6 ["students 請求生命週期"]
        Path6 --> ST_URL["students/urls.py"] --> ST_View["views.py"] --> ST_Tpl["student.html<br>enroll.html<br>timetable.html<br>grades_report.html<br>profile.html"]
    end

    class CoreURL coreStyle;
    class AdminApp,Path2,Path3,Path4,Path5,Path6 pathStyle;
    class MB_URL,US_URL,OF_URL,TC_URL,ST_URL appStyle;
    class MB_View,US_View,OF_View,TC_View,ST_View viewStyle;
    class MB_Tpl,US_Tpl,OF_Tpl,TC_Tpl,ST_Tpl templateStyle;

#數據庫連接圖

graph TD
    classDef mainTable fill:#e6f7ff,stroke:#1890ff,stroke-width:2px,color:#000;
    classDef joinTable fill:#fff0f6,stroke:#eb2f96,stroke-width:2px,color:#000;
    classDef independent fill:#f5f5f5,stroke:#d9d9d9,stroke-width:2px,color:#000;

    T[👨‍🏫 Teacher 老師表]:::mainTable
    C[🏢 SchoolClass 班級表]:::mainTable
    S[🎓 Student 學生表]:::mainTable
    CO[📚 Course 課程表]:::mainTable
    E[⚡ Enrollment 選課/成績表<br>多對多核心橋樑]:::joinTable
    ST[🧱 Staff 教職員表]:::independent

    T --> |"homeroom_teacher (外鍵)"| C
    C --> |"school_class (外鍵)"| S
    S --> |"student (外鍵)"| E
    CO --> |"course (外鍵)"| E

    class T,C,S,CO mainTable;
    class E joinTable;
    class ST independent;


```