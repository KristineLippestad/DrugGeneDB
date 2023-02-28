# Load the appropriate libraries
suppressMessages(library(dplyr))
library(tibble)
#install.packages("emba")
library(emba)
library(usefun)
#install.packages("PRROC")
library(PRROC)
library(DT)

predictionPreformance <- function(ensamblewiseSynergies, observedSynergiesFile, ROCFileName, PRFileName, ensembleswiseSynergiesFile, tableName){
  
  # Read ensemble-wise synergies file
  # `ss` => models trained to steady state
  ss_hsa_file = ensamblewiseSynergies
  ss_hsa_ensemblewise_synergies = emba::get_synergy_scores(ss_hsa_file)
  
  # Read observed synergies file
  observed_synergies_file = observedSynergiesFile
  observed_synergies = emba::get_observed_synergies(observed_synergies_file)
  # 1 (positive/observed synergy) or 0 (negative/not observed) for all tested drug combinations
  observed = sapply(ss_hsa_ensemblewise_synergies$perturbation %in% observed_synergies, as.integer)
  
  # Make a data table
  pred_hsa = dplyr::bind_cols(ss_hsa_ensemblewise_synergies %>% rename(ss_score = score),
                              tibble::as_tibble_col(observed, column_name = "observed"))
  sorted_pred_hsa <- pred_hsa %>% 
    as.data.frame() %>% 
    arrange(ss_score)
  write.table(sorted_pred_hsa, file = tableName, sep = "\t", quote = FALSE, row.names = F)
  

  # Visualize our prediction results in a table format
  DT::datatable(data = pred_hsa, options =
                  list(pageLength = 7, lengthMenu = c(7, 14, 21), searching = FALSE,
                       order = list(list(2, 'asc')))) %>%
    DT::formatRound(columns = 2, digits = 5) %>%
    DT::formatStyle(columns = 'observed',
                    backgroundColor = styleEqual(c(0, 1), c('white', '#ffffa1')))
  
  # Get ROC statistics (`roc_res$AUC` holds the ROC AUC)
  roc_res = usefun::get_roc_stats(df = pred_hsa, pred_col = "ss_score", label_col = "observed")
  
  # Plot ROC
  my_palette = RColorBrewer::brewer.pal(n = 9, name = "Set1")
  
  pdf(ROCFileName, width = 5, height = 5)
  plot(x = roc_res$roc_stats$FPR, y = roc_res$roc_stats$TPR,
       type = 'l', lwd = 3, col = my_palette[1], main = 'ROC curve, Ensemble-wise synergies (HSA)',
       xlab = 'False Positive Rate (FPR)', ylab = 'True Positive Rate (TPR)')
  legend('bottomright', title = 'AUC', col = my_palette[1], pch = 19,
         legend = paste(round(roc_res$AUC, digits = 2), "Calibrated"), cex = 1.3)
  grid(lwd = 0.5)
  abline(a = 0, b = 1, col = 'lightgrey', lty = 'dotdash', lwd = 1.2)
  dev.off()
  
  # Get PR statistics (`pr_res$auc.davis.goadrich` holds the PR AUC)
  # NOTE: PRROC considers by default that larger prediction values indicate the
  # positive class labeling. For us, the synergy scores belonging to the positive
  # or synergy class (observed = 1) are the lower ones, so we need to
  # reverse the scores to correctly calculate the PR curve
  pr_res = PRROC::pr.curve(scores.class0 = pred_hsa %>% pull(ss_score) %>% (function(x) {-x}),
                           weights.class0 = pred_hsa %>% pull(observed), curve = TRUE, rand.compute = TRUE)
  
  pdf(PRFileName, width = 5, height = 5)
  plot(pr_res, main = 'PR curve, Ensemble-wise synergies (HSA)',
       auc.main = FALSE, color = my_palette[1], rand.plot = TRUE)
  legend('topright', title = 'AUC', col = my_palette[1], pch = 19,
         legend = paste(round(pr_res$auc.davis.goadrich, digits = 2), "Calibrated"))
  grid(lwd = 0.5)
  dev.off()

} 
   
main <- function(){
  predictionPreformance("/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_main target/ags_cascade_1.0_ensemblewise_synergies.tab",'/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/observed_synergies', 'ROC_cas1.0_mainTarget_sort.pdf', 'PR_cas1.0_mainTarget_sort.pdf', "/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_main target/ags_cascade_1.0_ensemblewise_synergies.tab", "synergyTable_cas1.0_mainTarget_sort.txt")
  predictionPreformance("/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_10nM/ags_cascade_1.0_ensemblewise_synergies.tab",'/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/observed_synergies', 'ROC_cas1.0_10nM_sort.pdf', 'PR_cas1.0_10nM_sort.pdf', "/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_10nM/ags_cascade_1.0_ensemblewise_synergies.tab", "synergyTable_cas1.0_10nM_sort.txt")
  predictionPreformance("/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_100nM/ags_cascade_1.0_ensemblewise_synergies.tab",'/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/observed_synergies', 'ROC_cas1.0_100nM_sort.pdf', 'PR_cas1.0_100nM_sort.pdf', "/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_100nM/ags_cascade_1.0_ensemblewise_synergies.tab", "synergyTable_cas1.0_100nM_sort.txt")
  predictionPreformance("/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_1uM/ags_cascade_1.0_ensemblewise_synergies.tab",'/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/observed_synergies', 'ROC_cas1.0_1uM_sort.pdf', 'PR_cas1.0_1uM_sort.pdf', "/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_1uM/ags_cascade_1.0_ensemblewise_synergies.tab", "synergyTable_cas1.0_1uM_sort.txt")
  predictionPreformance("/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_10uM/ags_cascade_1.0_ensemblewise_synergies.tab",'/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/observed_synergies', 'ROC_cas1.0_10uM_sort.pdf', 'PR_cas1.0_10uM_sort.pdf', "/Users/kristinelippestad/druglogics-synergy/ags_cascade_1.0/ags_cascade_1.0_10uM/ags_cascade_1.0_ensemblewise_synergies.tab", "synergyTable_cas1.0_10uM_sort.txt")
}

main()
