# Question wording: spec draft vs adopted

_Run `wording_probe` finished 2026-10-22 17:36:36 (arm64)._

## Arguments

- `threshold`: `0.6`
- `date`: `2026-10-22`

## Summary

```
0. DICE: scene actions vs categories  pick/confidence; * = wrong or confidence < 0.6
   expected       line                                                      actions      categories
   ask-guard      I ask the guard what the town is called           ask-guard/0.98       talk/0.77 
   present-token  I show him the pass the merchant gave me      present-token/0.95      bluff/0.49*
   loiter         I sort of edge towards the gate while hummin         loiter/0.94       move/0.36*
   push-past      I draw my cloak around me and shove the guar      push-past/0.97     attack/0.64 
   talk-jailer    I look around and ask whoever is nearest whe    talk-jailer/0.64       talk/0.60*
   claim-rank     I tell the guard I'm the mayor's nephew           ask-guard/0.55*     bluff/0.42*
   give-item      I give the guard one copper coin                  give-item/0.97        use/0.51*
   walk-through   I walk through the gate into the market        walk-through/0.98       move/0.76 
   buy            I buy the brass key                                     buy/0.85       take/0.83 
   hit-someone    I punch the merchant                            hit-someone/0.86     attack/0.84 
   talk-child     I ask the child what she knows                   talk-child/0.97       talk/0.69 
   steal          I grab the key and run                                steal/0.64       take/0.49*
   go-elsewhere   I head to the inn                              go-elsewhere/0.96       move/0.78 
   impossible     I fly over the town wall                         impossible/0.99      other/0.30*
   impossible     I pay the guard ten gold coins                   impossible/0.82        use/0.23*
   impossible     I teleport out of the cell                       impossible/0.78      other/0.28*
   impossible     I cast a spell to open the locked box            impossible/0.92        use/0.22*
   right and confident: actions 16/17, categories 7/17 (category judged on the action's type)
   the five demo lines, actions dice: 5/5 right with confidence >= 0.6
   impossible attempts sent to the `impossible` action: 4/4

0b. NOT-POSSIBLE AS AN OUTCOME OPTION (replaced)  outcome pick/confidence; * = wrong or < 0.6
   guard-asks-business/guard-chats      I ask the guard what the town is called   guard-asks-business/0.75 
   guard-suspicious                     I show him the pass the merchant gave me     guard-suspicious/0.35*
   guard-stops-you/walk-the-wall        I sort of edge towards the gate while hu    not-possible-here/0.22*
   guard-overpowers-you/you-flee        I draw my cloak around me and shove the     not-possible-here/0.89*
   jailer-ignores                       I look around and ask whoever is nearest    not-possible-here/0.59*
   not-possible-here                    I fly over the town wall                    not-possible-here/0.74 
   not-possible-here                    I pay the guard ten gold coins              not-possible-here/0.78 
   not-possible-here                    I walk out of the cell door                 not-possible-here/0.40*
   not-possible-here                    I cast a spell to open the locked box       not-possible-here/0.46*
   right and confident: 3/9

1. CATEGORY DICE  pick/confidence, spec options vs tuned (questions.yaml dice_categories)
   expected line                                                   spec        adopted
   talk     I ask the guard what the town is called           talk/0.76      talk/0.77
   bluff    I show him the pass the merchant gave me           use/0.43     bluff/0.49
   ?        I sort of edge towards the gate while hummin      move/0.35      move/0.36
   attack   I draw my cloak around me and shove the guar    attack/0.63    attack/0.64
   bluff    I tell the guard I'm the mayor's nephew          bluff/0.45     bluff/0.41
   use      I give the guard one copper coin                   use/0.54       use/0.51
   move     I walk through the gate into the market           move/0.74      move/0.76
   take     I buy the brass key                               take/0.83      take/0.83
   attack   I punch the merchant                            attack/0.83    attack/0.84
   talk     I ask the child what she knows                    talk/0.70      talk/0.70
   take     I grab the key and run                            take/0.46      take/0.49
   move     I head to the inn                                 move/0.77      move/0.77

2. LEDGER CLAIMS  p(established); * = wrong side or confidence < 0.6
   action in state: "I show him the pass the merchant gave me"
   truth/claim                                   with action  ledger only
   T the player has three copper coins                 0.76*        0.87 
   T the player has a travelling cloak                 0.78*        0.87 
   T the merchant is selling a brass key               0.81         0.82 
   T the player arrived on foot                        0.81         0.88 
   F the merchant gave the player a pass               0.23*        0.10 
   F the player holds a brass key                      0.37*        0.54*
   F the player knows the sergeant                     0.09         0.10 
   F the player has a sword                            0.09         0.10 
   right and confident: with action 4/8, ledger only 7/8

3. ALLOWED (retired)  Decider p(true) [* = wrong or unsure] and Nova Lite answer [! = wrong]
   truth/line                                       spec D  Nova  adopted D  Nova
   T I ask the guard what the town is called         0.29*    T       0.80*    T 
   T I show him the pass the merchant gave me        0.23*    T       0.73*    T 
   T I sort of edge towards the gate while hummin    0.23*    T       0.72*    T 
   T I draw my cloak around me and shove the guar    0.20*    F!      0.81     T 
   T I punch the merchant                            0.25*    F!      0.80     T 
   T I grab the key and run                          0.21*    F!      0.53*    T 
   F I fly over the town wall                        0.18     F       0.55*    F 
   F I pay the guard ten gold coins                  0.17     F       0.65*    F 
   F I walk out of the cell door                     0.21*    F       0.43*    F 
   F I cast a spell to open the locked box           0.21*    F       0.49*    F 
   Decider right and confident: spec 2/10, adopted 2/10. Nova Lite right: spec 7/10, adopted 10/10

4. DANGER (retired)  expected value / confidence, and P(level >= 3)
   line                                                      spec levels           adopted levels
   I ask the guard what the town is called             1.5/0.45 P≥3=0.26        1.4/0.40 P≥3=0.25
   I show him the pass the merchant gave me            1.9/0.45 P≥3=0.33        1.9/0.40 P≥3=0.32
   I sort of edge towards the gate while hummin        1.6/0.45 P≥3=0.26        1.5/0.39 P≥3=0.27
   I draw my cloak around me and shove the guar        2.5/0.45 P≥3=0.50        3.0/0.46 P≥3=0.69
   I tell the guard I'm the mayor's nephew             1.9/0.46 P≥3=0.33        1.7/0.42 P≥3=0.28
   I give the guard one copper coin                    1.8/0.45 P≥3=0.31        2.0/0.42 P≥3=0.34
   I walk through the gate into the market             1.7/0.46 P≥3=0.29        1.6/0.36 P≥3=0.31
   I buy the brass key                                 1.8/0.43 P≥3=0.33        1.8/0.45 P≥3=0.31
   I punch the merchant                                2.6/0.47 P≥3=0.54        2.7/0.40 P≥3=0.59
   I ask the child what she knows                      1.5/0.44 P≥3=0.26        1.4/0.45 P≥3=0.23
   I grab the key and run                              2.3/0.45 P≥3=0.45        2.0/0.43 P≥3=0.38
   I head to the inn                                   1.7/0.45 P≥3=0.30        1.4/0.41 P≥3=0.27
   highest danger confidence seen in either wording: 0.47 (threshold 0.6)
```

Rows: `results/wording_probe.jsonl`

## Notes

Spec wording is the first draft in SPEC_hobson.md; adopted wording is hobson/questions.yaml.
