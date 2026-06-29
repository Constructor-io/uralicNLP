build_wheel:
	pip wheel . --no-deps -w dist/


login_twine:
	aws codeartifact login --tool twine --domain constructor --repository constructor

push_wheel:login_twine
	uv tool run twine upload --repository codeartifact --verbose "dist/*.whl"

clean:
	rm -rf dist/

