###########################################################
### Class for analysis of scoring results generated in Py
###
###########################################################

library(ggplot2)
library(scales)

data <- read.csv("../data/output/score.tsv", header = TRUE, sep = "\t" , stringsAsFactors = FALSE)

# apply numeric to approrpiate cols, remove ids
data$avg_renter_income <- as.numeric(data$avg_renter_income)
data$avg_renter_density <- as.numeric(data$avg_renter_density)
data$renter_pop_est <- as.numeric(data$renter_pop_est)

# begin plots
ggplot(data) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point(aes(size=score)) +
    geom_text(check_overlap = TRUE, size=2, nudge_x=0.025, aes(color=renter_pop_est)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 4p+\nRenter Density") +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)")
    theme(legend.position="bottom")
