# usage

login to Freshbooks and copy the bearer token from the a call to the API, then from the
command line

$ watson log --from 2022-08-09 --to 2022-08-31 -T YK --json | ./toFreshbooks.py 

