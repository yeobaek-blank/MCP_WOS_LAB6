# mcp_server.py

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from collections import Counter

csv_path = '통합 문서1.csv'
df = pd.read_csv(csv_path)

SEARCH_COLUMNS = [
    'Authors',
    'Author Full Names',
    'Article Title',
    'Source Title',
    'Book Series Title',
    'Language',
    'Author Keywords',
    'Abstract'
]

app = Flask(__name__)

@app.route('/keyword_stats', methods=['GET'])
def keyword_stats():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({'error': 'keyword parameter required'}), 400

    valid_columns = [col for col in SEARCH_COLUMNS if col in df.columns]
    if not valid_columns:
        return jsonify({'error': 'No valid columns to search.'}), 400

    # 여러 컬럼 중 하나라도 키워드가 포함된 행을 찾음 (OR 조건)
    mask = False
    for col in valid_columns:
        mask = mask | df[col].fillna('').str.contains(keyword, case=False, na=False)

    filtered = df[mask]

    # 검색 결과 샘플 (최대 20개, NaN 값은 None으로 바꿔주기)
    result = (
        filtered.head(20)
        .replace({np.nan: None, pd.NA: None, pd.NaT: None})
        .to_dict(orient='records')
    )

    # 연도별 언급 통계
    yearly_trend = {}
    if 'Publication Year' in filtered.columns:
        yearly_trend = filtered['Publication Year'].value_counts().sort_index().to_dict()

    # 저자별 키워드 언급 횟수
    top_authors = []
    if 'Authors' in filtered.columns:
        authors_list = filtered['Authors'].dropna().str.split(',')
        all_authors = [author.strip() for sublist in authors_list for author in sublist]
        top_authors = Counter(all_authors).most_common(10)
        top_authors = [{'author': name, 'count': cnt} for name, cnt in top_authors]

    return jsonify({
        'result': result,
        'yearly_trend': yearly_trend,
        'top_authors': top_authors
    })

def get_app():
    return app
