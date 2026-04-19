# Feature Preview Before Classifier Fit

This preview is generated for inspection only. It is not reused by CV training, so it does not change validation behavior.

## Feature Block Summary

```text
       feature_block  rows  columns
cleaned_text_preview   510     12.0
   metadata_features   510     67.0
         title_tfidf   510  17365.0
 title_tfidf_nonzero 84230      NaN
```

## Cleaned Raw Fields

```text
 id  Label                                                                                 title_raw                                                                             title_clean venue_raw venue_clean                                                             authors_raw                                                             authors_parsed              doi_raw doi_prefix doi_suffix_head  doi_suffix_head_missing
299      1                                                Tabled CLP for Reasoning Over Stream Data.                                              tabled clp for reasoning over stream data.      iclp        iclp                                              Edmond Jajaga, Lule Ahmedi                                                edmond jajaga | lule ahmedi 10.1109/icsc.2017.64    10.1109            icsc                        0
 92      5 XAI-LAW: A Logic Programming Tool for Modeling, Explaining, and Learning Legal Decisions. xai-law: a logic programming tool for modeling explaining and learning legal decisions.      iclp        iclp Agostino Dovier, Talissa Dreossi, Andrea Formisano, Benedetta Strizzolo agostino dovier | talissa dreossi | andrea formisano | benedetta strizzolo 10.4204/eptcs.439.28    10.4204           eptcs                        0
```

## Metadata Features

```text
 title_char_count  title_word_count  title_avg_word_length  title_has_colon  title_has_question  year_is_missing  year_normalized  paper_age  has_doi  doi_length  doi_digit_count  doi_slash_count  doi_dot_count  doi_suffix_head_missing  venue_iclp  venue_kr  doi_prefix_10.1002  doi_prefix_10.1007  doi_prefix_10.1016  doi_prefix_10.1017  doi_prefix_10.1093  doi_prefix_10.1098  doi_prefix_10.1109  doi_prefix_10.1145  doi_prefix_10.1201  doi_prefix_10.14711  doi_prefix_10.1484  doi_prefix_10.1515  doi_prefix_10.1609  doi_prefix_10.1613  doi_prefix_10.20944  doi_prefix_10.21236  doi_prefix_10.2139  doi_prefix_10.24963  doi_prefix_10.25368  doi_prefix_10.29007  doi_prefix_10.3233  doi_prefix_10.3403  doi_prefix_10.4018  doi_prefix_10.4204  doi_prefix_10.4324  doi_prefix_10.5220  doi_prefix_10.7551  doi_prefix___rare__  doi_suffix_head___missing__  doi_suffix_head___rare__  doi_suffix_head_aaai  doi_suffix_head_ada  doi_suffix_head_aic  doi_suffix_head_b  doi_suffix_head_bfb  doi_suffix_head_c  doi_suffix_head_cbo  doi_suffix_head_ch  doi_suffix_head_eptcs  doi_suffix_head_ijcai  doi_suffix_head_j  doi_suffix_head_jair  doi_suffix_head_kr  doi_suffix_head_m  doi_suffix_head_mitpress  doi_suffix_head_oso  doi_suffix_head_preprints  doi_suffix_head_rsos  doi_suffix_head_s  doi_suffix_head_ssrn  doi_suffix_head_thesis
               42                 7               5.142857                0                   0                0        -2.662140       10.0        1          20               12                1              3                        0           1         0                   0                   0                   0                   0                   0                   0                   1                   0                   0                    0                   0                   0                   0                   0                    0                    0                   0                    0                    0                    0                   0                   0                   0                   0                   0                   0                   0                    0                            0                         1                     0                    0                    0                  0                    0                  0                    0                   0                      0                      0                  0                     0                   0                  0                         0                    0                          0                     0                  0                     0                       0
               89                12               6.500000                1                   0                0         0.971289        1.0        1          20               11                1              3                        0           1         0                   0                   0                   0                   0                   0                   0                   0                   0                   0                    0                   0                   0                   0                   0                    0                    0                   0                    0                    0                    0                   0                   0                   0                   1                   0                   0                   0                    0                            0                         0                     0                    0                    0                  0                    0                  0                    0                   0                      1                      0                  0                     0                   0                  0                         0                    0                          0                     0                  0                     0                       0
```

## Top Title TF-IDF Terms

```text
 row  id  Label                      term    tfidf
   0 299      1         word__stream data 0.363247
   0 299      1                 word__clp 0.363247
   0 299      1       word__clp reasoning 0.363247
   0 299      1          word__tabled clp 0.363247
   0 299      1              word__tabled 0.363247
   0 299      1    word__reasoning stream 0.363247
   0 299      1              word__stream 0.324767
   0 299      1                word__data 0.263777
   0 299      1           word__reasoning 0.182374
   0 299      1                char__bled 0.162262
   0 299      1               char__bled  0.162262
   0 299      1               char__abled 0.162262
   1  92      5       word__tool modeling 0.266907
   1  92      5    word__programming tool 0.266907
   1  92      5           word__law logic 0.266907
   1  92      5             word__xai law 0.266907
   1  92      5      word__learning legal 0.266907
   1  92      5     word__legal decisions 0.266907
   1  92      5 word__explaining learning 0.266907
   1  92      5 word__modeling explaining 0.266907
   1  92      5                 word__xai 0.250367
   1  92      5           word__decisions 0.238632
   1  92      5               word__legal 0.229530
   1  92      5                 word__law 0.229530
```