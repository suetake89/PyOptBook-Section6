# problem.py

import pandas as pd
import pulp


class CarGroupProblem():
    """学生の乗車グループ分け問題を解くクラス"""
    def __init__(self, students_df, cars_df, name='ClubCarProblem'):
        # 初期化メソッド
        self.student_df = students_df
        self.car_df = cars_df
        self.name = name
        self.problem = self._formulate()

    def _formulate(self):
        # 学生の乗車グループ分け問題（0-1整数計画問題）のインスタンス作成
        problem = pulp.LpProblem(self.name, pulp.LpMinimize)


        # 生徒のリスト
        S = self.student_df['student_id'].tolist()
        # 車のリスト
        C = self.car_df['car_id'].tolist()
        # 生徒と車のペアのリスト
        SC = [(s,c) for s in S for c in C]
        # 学年のリスト
        G = [1, 2, 3, 4]

        U = self.car_df['capacity'].to_list()

        S_male = [row.student_id for row in self.student_df.itertuples() if row.gender==0]
        S_female = [row.student_id for row in self.student_df.itertuples() if row.gender==1]
        S_g = {g: [row.student_id for row in self.student_df.itertuples() if row.grade==g] for g in G}

        S_license = [row.student_id for row in self.student_df.itertuples() if row.license==1]

        # 変数の辞書を作成
        x = {}
        # 車cに生徒sが乗るかを表す変数x_(s,c)を作成
        for s, c in SC:
            # LpVariableクラスに変数名と非負であるということと連続変数であることを指定する
            x[s, c] = pulp.LpVariable(f'x_{s}{c}', lowBound=0, cat='Binary')

        # 制約
        # (1) 各学生を１つの車に割り当てる
        for s in S:
            problem += pulp.lpSum(x[s, c] for c in C) == 1
            
        # (2) 法規制に関する制約：各車には乗車定員より多く乗ることができない
        for c in C:
            problem += pulp.lpSum(x[s, c] for s in S) <= U[c]

        # (3) 法規制に関する制約：各車にドライバーを1人以上割り当てる
        for c in C:
            problem += pulp.lpSum(x[s, c] for s in S_license) >= 1

        # (4) 懇親を目的とした制約: 各車に各学年の学生を１人以上割り当てる
        for c in C:
            for g in G:
                problem += pulp.lpSum(x[s, c] for s in S_g[g]) >= 1

        # (5) 各車に男性を1人以上割り当てる
        for c in C:
            problem += pulp.lpSum(x[s, c] for s in S_male) >= 1

        # (6) 各車に女性を1人以上割り当てる
        for c in C:
            problem += pulp.lpSum(x[s, c] for s in S_female) >= 1

        # (7) 各車に連続した学籍番号の人は載せない
        for s, c in SC:
            if s + 1 in S:
                problem += x[s, c] + x[s+1, c] <= 1

        
        # 最適化後に利用するデータを返却
        return {'prob': problem, 'variable': {'x': x}, 'list': {'S': S, 'C': C}}

    def solve(self):
        # 最適化問題を解くメソッド
        # 問題を解く
        status = self.problem['prob'].solve()

        # 最適化結果を格納
        x = self.problem['variable']['x']
        S = self.problem['list']['S']
        C = self.problem['list']['C']
        car2students = {c: [s for s in S if x[s, c].value() == 1] for c in C}
        student2car = {s: c for c, ss in car2students.items() for s in ss}
        solution_df = pd.DataFrame(list(student2car.items()), columns=['student_id', 'car_id'])

        return solution_df


if __name__ == '__main__':
    # データの読み込み
    students_df = pd.read_csv('resource/students.csv')
    cars_df = pd.read_csv('resource/cars.csv')

    # 数理モデル インスタンスの作成
    problem = CarGroupProblem(students_df, cars_df)

    # 問題を解く
    solution_df = problem.solve()

    # 結果の表示
    print('Solution: \n', solution_df)