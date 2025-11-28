dataset: ./scripts/*.sh
		cd scripts && \
		bash ./make_pytorch_dataset_dir_from_adfa.sh && \
		bash ./longest_element.sh

rnn_syscall_classifier.pt:
	python3 model.py

check_log:
	python3 ./check_log.py $(LOG_FILENAME)

trace:
	./trace.sh $(PROG_NAME)

help:
	@echo "targets:\n\
		dataset: format and place the dataset that is assumed to reside in DATASET_DIR in ./scripts/variables.sh\n\
		rnn_syscall_classifier: train on dataset and save the model\n\
		check_log LOG_FILENAME=<LOG_FILENAME>: use the model to classify the LOG_FILENAME\n\
		trace PROG_NAME=[<PROG_NAME> || ALL]: trace the program called PROG_NAME, may produce multiple log files if multiple instances found\n\
		                OUTPUT: PID.log per found instance\n\
                        If PROG_NAME is set to ALL, all programs are traced\n\
		"


