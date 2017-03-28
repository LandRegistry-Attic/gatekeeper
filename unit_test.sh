export PYTHONPATH=.

reportflag=off

# Check if there's a -r argument (the only one supported) and set a flag if so
while [ $# -gt 0 ]
do
    case "$1" in
        -r)  reportflag=on;;
        *)
            echo >&2 "usage: $0 [-r]"
	        exit 1;;
    esac
    shift
done

# If the report flag is set generate report output otherwise just run the tests
if [ "$reportflag" = on ] ; then
    py.test unit_tests --junitxml=test-output/unit-test-output.xml --cov-report=html:test-output/unit-test-cov-report
else
    py.test unit_tests
fi
