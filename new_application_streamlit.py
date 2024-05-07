
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import japanize_matplotlib

from problem import CarGroupProblem

def preprocess(students, cars):
    students_df = pd.read_csv(students)
    cars_df = pd.read_csv(cars)
    return students_df, cars_df

def convert_to_csv(df):
    return df.to_csv().encode('utf-8')

def draw_pie_charts(gender_data, grade_data, car_id):
    # 2つの円グラフを作成
    fig, axes = plt.subplots(1, 2, figsize=(10, 5)) 
    axes[0].pie(gender_data, labels=gender_data.index, autopct='%1.1f%%', startangle=90)
    axes[0].set_title(f'Car ID {car_id} - 男女比率')
    axes[0].axis('equal') 

    axes[1].pie(grade_data, labels=grade_data.index, autopct='%1.1f%%', startangle=90)
    axes[1].set_title(f'Car ID {car_id} - 学年比率')
    axes[1].axis('equal')

    plt.tight_layout()
    st.pyplot(fig)

# アプリのタイトルを設定
st.title("乗車グループ分けの最適化アプリ")

# タブの作成
tab1, tab2, tab3 = st.tabs(["データ入力", "最適化実行", "結果の可視化"])

# タブ1: データ入力
with tab1:
    with st.form("upload_form"):
        students = st.file_uploader("学生データをアップロード", type='csv', help="CSVファイルのみ、最大200MB")
        cars = st.file_uploader("車データをアップロード", type='csv', help="CSVファイルのみ、最大200MB")
        submitted = st.form_submit_button("データアップロード")
        if submitted and students and cars:
            students_df, cars_df = preprocess(students, cars)
            st.session_state['students_df'] = students_df
            st.session_state['cars_df'] = cars_df
            st.success("データアップロード完了！")

# タブ2: 最適化実行
with tab2:
    if 'students_df' in st.session_state and 'cars_df' in st.session_state:
        if st.button("最適化を実行"):
            solution_df = CarGroupProblem(st.session_state['students_df'], st.session_state['cars_df']).solve()
            st.session_state['solution_df'] = solution_df
            st.write("#### 最適化結果")
            csv = convert_to_csv(solution_df)
            st.download_button(
                "Press to Download",
                csv,
                "solution.csv",
                "text/csv",
                key="download-csv"
            )
            st.write(solution_df)
    else:
        st.error("データを先にアップロードしてください。")

# タブ3: 結果の可視化
with tab3:
    if 'students_df' in st.session_state and 'solution_df' in st.session_state:
        # solution_df と students_df をマージ
        merge_df = st.session_state['solution_df'].merge(st.session_state['students_df'], on='student_id')
        grouped = merge_df.groupby('car_id')

        for car_id, group in grouped:
            # 男女比データの準備
            gender_counts = group['gender'].value_counts()
            gender_labels = {0: "男性", 1: "女性"}
            gender_counts.index = [gender_labels[idx] for idx in gender_counts.index]

            # 学年比データの準備
            grade_counts = group['grade'].value_counts()
            grade_labels = {1: "１年生", 2: "２年生", 3: "３年生", 4: "４年生"}
            grade_counts.index = [grade_labels[idx] for idx in grade_counts.index]

            draw_pie_charts(gender_counts, grade_counts, car_id)
    else:
        st.error("データを先にアップロードして、最適化を実行してください。")