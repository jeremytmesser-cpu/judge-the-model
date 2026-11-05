# Decisions

<!-- Fill in each section at the step the activity website gives, then commit and push.
     Write each answer after its label. Keep the headings and labels exactly as they are:
     `python -m analysis` reads them. Limit: 150 words for Before results.
     Fill in Recommendations and Design choice and AI use last, once your app is built. -->

## Before results
For each dataset: positive class; which error matters more for the job (missed positive or false alarm) and why.
- readmission: Readmitted within 30 days. Missing a true readmission matters more than a false alarm because a patient who needs extra follow-up after discharge can be missed and then deteriorate; a false alarm mainly triggers extra review rather than harm.
- diabetes: Doctor diagnosis or HbA1c ≥ 6.5%. Missing a true positive matters more because the goal is to find adults who need follow-up testing or treatment; a false alarm usually leads to an extra check rather than a serious clinical consequence.

## Recommendations
- readmission: Logistic regression at a moderate threshold, around 0.40, because it has the strongest test AUROC and is easier to interpret than the more complex models, but it should still be used with clinician review because no model is strong enough for fully automatic discharge decisions.
- diabetes: Logistic regression at a moderate threshold, around 0.35, because it performs best on the test set and the cost of missing a positive case is higher than the cost of a false alarm; the threshold should be tuned to prioritize sensitivity while keeping the flagged group manageable.

## Design choice and AI use
A few sentences each. The design choice must be your own idea, not an AI tool's.
- design choice: I chose to show a threshold slider beside the confusion matrix so the clinical lead can see how changing the cut-off shifts missed positives, false alarms, and flagged patients in real time; this makes the decision trade-off visible without relying on accuracy alone.
- AI suggestion I turned down: “Just show accuracy for each model.” I did not use it because accuracy hides the clinically important difference between missing a patient who needs follow-up and over-flagging people, and the activity is specifically about understanding the trade-off between those errors.
