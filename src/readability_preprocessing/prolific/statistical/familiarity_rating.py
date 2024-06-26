from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_rating_std_grouped
from readability_preprocessing.prolific.statistical.statistical_tests import (
    anova,
    equivalence,
)

snippets = load_combined()
java_knowledge_question_id = 16
tuples = question_rating_std_grouped(snippets, java_knowledge_question_id)
anova(tuples)
equivalence(tuples)
