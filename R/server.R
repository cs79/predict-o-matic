# server setup
source("predict.R")
column_classes = c("integer", "character", "integer", "integer", "character", "character")
dict = read.csv("lookup_outfile_CLEAN.csv", colClasses = column_classes)
dict = dict[complete.cases(dict), ]

shinyServer(function(input, output) {
    # pass input to predict function, render top prediction and plot the runners up
    observeEvent(input$predictNow, {
        output$pred0 <- renderText({ predict_v3(input$textToPredict, dict = dict)[1] })
        output$plot <- renderPlot({ plot_preds_v2(input$textToPredict, dict=dict) }, height= 250)
    })
})
