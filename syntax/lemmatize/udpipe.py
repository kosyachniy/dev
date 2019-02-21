def lemmatize(word, modelfile='../russian-syntagrus-ud-2.3-181115.udpipe'):
	from ufal.udpipe import Model, Pipeline
	model = Model.load(modelfile)
	pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

	processed = pipeline.process(word)

	output = [l for l in processed.split('\n') if not l.startswith('#')]
	tagged = [w.split('\t')[2] for w in output if w]

	return tagged