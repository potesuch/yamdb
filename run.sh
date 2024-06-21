rm -f /app/infra/pytest.ini
rm -rf /app/infra/tests

cp infra/pytest.ini /app/infra/pytest.ini
cp -a infta/tests/ /app/infra/tests

cd /app
pip3 install -r requirements.txt
pytest
