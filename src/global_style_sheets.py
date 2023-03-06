
"#231f20"
"#40383B"
"#8d8d92"
"1A1718"
"lightgray"
"rgb(230, 230, 230)"

TAB_STYLE: str = """
QTabWidget::pane {
  border: 1px solid #110E0F;
  top:-1px; 
  background-color: #231f20; 
} 

QTabBar::tab {
  background: rgb(230, 230, 230); 
  border: 1px solid lightgray; 
  padding: 8px;
} 

QTabBar::tab:selected { 
  background: rgb(245, 245, 245); 
  margin-bottom: -1px; 
}
"""

SCROLL_AREA: str = """
QScrollArea {
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: #1A1718;
}

QScrollBar::handle:vertical {
    background-color: #8d8d92;
}
"""
