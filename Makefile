build:
	poetry build
	ls -lt dist | grep "tar.gz" | head -n 1 |awk '{print "./dist/"$$9}' |xargs pip install


publish:
	poetry publish

publish-custom:
	poetry publish -r my-custom-repo