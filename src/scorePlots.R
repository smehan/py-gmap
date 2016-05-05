###########################################################
### Class for analysis of scoring results generated in Py
###
###########################################################

# standard libs
# 3rd party
library(ggplot2)
library(scales)
library(ggrepel)

# read in df
scores <- read.csv("../data/output/score.tsv", header = TRUE, sep = "\t" , stringsAsFactors = FALSE)

# apply numeric to approrpiate cols, remove ids
scores$avg_renter_income <- as.numeric(scores$avg_renter_income)
scores$avg_renter_density <- as.numeric(scores$avg_renter_density)
scores$renter_pop_est <- as.numeric(scores$renter_pop_est)
scores$id <- NULL
scores$plid <- NULL

# begin plots
ggplot(scores) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point(aes(size=score)) +
    geom_jitter() +
    geom_text(check_overlap = TRUE,
              size=2,
              #nudge_x=0.025,
              aes(color=renter_pop_est),
              position = position_jitter(width=1, height=0)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Mean 4p+\nRenter Density") +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)") +
    theme(axis.text.x = element_text(angle = 90)) +
    theme(strip.text.x = element_text(colour = "red", angle = 0, size = 8, hjust = 0.5, vjust = 0.5)) +
    theme(axis.title.y = element_text(vjust=1.0)) +
    theme(axis.title.x = element_text(vjust=-0.1)) +
    theme(plot.title = element_text(size=12, face="bold", vjust=2)) +
    theme(legend.position="bottom")

# two plots with score as label size, then the same two without size
ggplot(scores) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point() +
    geom_label_repel(size=scores$score,
                     aes(color=renter_pop_est,
                         size=score)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Estimated Renter Population") +
    scale_size(range = c(5, 10)) +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY\nScores by Label Size") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)") +
    theme(axis.text.x = element_text(angle = 90)) +
    theme(strip.text.x = element_text(colour = "red", angle = 0, size = 8, hjust = 0.5, vjust = 0.5)) +
    theme(axis.title.y = element_text(vjust=1.0)) +
    theme(axis.title.x = element_text(vjust=-0.1)) +
    theme(legend.text = element_text(colour = 'red', angle = 90, size = 10, hjust = 0, vjust = 3, face = 'bold')) +
    theme(plot.title = element_text(size=12, face="bold", vjust=2)) +
    theme(legend.position="bottom")

ggplot(scores) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point() +
    geom_label_repel(size=scores$score,
                     aes(color=renter_pop_est,
                         size=score)) +
    facet_wrap(~target.zip) +
    scale_colour_gradientn(colours=rainbow(4), name = "Estimated Renter Population") +
    scale_size(range = c(5, 10)) +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY\nScores by Label Size") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)") +
    theme(axis.text.x = element_text(angle = 90)) +
    theme(strip.text.x = element_text(colour = "red", angle = 0, size = 8, hjust = 0.5, vjust = 0.5)) +
    theme(axis.title.y = element_text(vjust=1.0)) +
    theme(axis.title.x = element_text(vjust=-0.1)) +
    theme(legend.text = element_text(colour = 'red', angle = 0, size = 10, hjust = 0, vjust = 3, face = 'bold')) +
    theme(plot.title = element_text(size=12, face="bold", vjust=2))

ggplot(scores) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point() +
    geom_label_repel(aes(color=renter_pop_est)) +
    scale_colour_gradientn(colours=rainbow(4), name = "Estimated Renter Population") +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)") +
    theme(axis.text.x = element_text(angle = 90)) +
    theme(strip.text.x = element_text(colour = "red", angle = 0, size = 8, hjust = 0.5, vjust = 0.5)) +
    theme(axis.title.y = element_text(vjust=1.0)) +
    theme(axis.title.x = element_text(vjust=-0.1)) +
    theme(legend.text = element_text(colour = 'red', angle = 90, size = 10, hjust = 0, vjust = 3, face = 'bold')) +
    theme(plot.title = element_text(size=12, face="bold", vjust=2)) +
    theme(legend.position="bottom")

ggplot(scores) +
    aes(x=avg_renter_density, y=avg_renter_income, label=name) +
    geom_point() +
    geom_label_repel(aes(color=renter_pop_est)) +
    facet_wrap(~target.zip) +
    scale_colour_gradientn(colours=rainbow(4), name = "Estimated Renter Population") +
    ggtitle("Distribution of Laundries in Targeted Areas\nin Nassau County, NY") +
    labs(x="Mean Normalized Renter Density", y="Mean Renter Income ($)") +
    theme(axis.text.x = element_text(angle = 90)) +
    theme(strip.text.x = element_text(colour = "red", angle = 0, size = 8, hjust = 0.5, vjust = 0.5)) +
    theme(axis.title.y = element_text(vjust=1.0)) +
    theme(axis.title.x = element_text(vjust=-0.1)) +
    theme(legend.text = element_text(colour = 'red', angle = 0, size = 10, hjust = 0, vjust = 3, face = 'bold')) +
    theme(plot.title = element_text(size=12, face="bold", vjust=2))

