from pydantic import BaseModel, Field
from typing import Optional, List


class OfficerTitle(BaseModel):
    start_year: str = Field(alias="startYear")
    start_month: str = Field(alias="startMonth")
    start_day: str = Field(alias="startDay")
    id1: str = Field(alias="iD1")
    abbr1: str = Field(alias="abbr1")
    id2: str = Field(alias="iD2")
    abbr2: str = Field(alias="abbr2")
    value: str = Field(alias="Value")

class Officer(BaseModel):
    rank: int
    since: str
    first_name: str = Field(alias="firstName")
    mi: Optional[str] = Field(alias="mI")
    last_name: str = Field(alias="lastName")
    age: Optional[str]
    title: OfficerTitle

class Officers(BaseModel):
    officer: List[Officer]

class PeerCompany(BaseModel):
    ticker_id: str = Field(alias="tickerId")
    company_name: str = Field(alias="companyName")
    price_to_book_value_ratio: Optional[float] = Field(None, alias="priceToBookValueRatio")
    price_to_earnings_value_ratio: Optional[float] = Field(None, alias="priceToEarningsValueRatio")
    market_cap: Optional[float] = Field(None, alias="marketCap")
    price: Optional[float] = None
    percent_change: Optional[float] = Field(None, alias="percentChange")
    net_change: Optional[float] = Field(None, alias="netChange")
    return_on_average_equity_5year_average: Optional[float] = Field(None, alias="returnOnAverageEquity5YearAverage")
    return_on_average_equity_trailing12_month: Optional[float] = Field(None, alias="returnOnAverageEquityTrailing12Month")
    lt_debt_per_equity_most_recent_fiscal_year: Optional[float] = Field(None, alias="ltDebtPerEquityMostRecentFiscalYear")
    net_profit_margin_5year_average: Optional[float] = Field(None, alias="netProfitMargin5YearAverage")
    net_profit_margin_percent_trailing12_month: Optional[float] = Field(None, alias="netProfitMarginPercentTrailing12Month")
    dividend_yield_indicated_annual_dividend: Optional[float] = Field(None, alias="dividendYieldIndicatedAnnualDividend")
    total_shares_outstanding: Optional[float] = Field(None, alias="totalSharesOutstanding")
    language_support: Optional[str] = Field(None, alias="languageSupport")
    image_url: Optional[str] = Field(None, alias="imageUrl")
    overall_rating: Optional[str] = Field(None, alias="overallRating")
    yhigh: Optional[float] = None
    ylow: Optional[float] = None

class CompanyProfile(BaseModel):
    company_description: Optional[str] = Field(None, alias="companyDescription")
    mg_industry: Optional[str] = Field(None, alias="mgIndustry")
    is_in_id: Optional[str] = Field(None, alias="isInId")
    officers: Optional[Officers] = None
    exchange_code_bse: Optional[str] = Field(None, alias="exchangeCodeBse")
    exchange_code_nse: Optional[str] = Field(None, alias="exchangeCodeNse")
    peer_company_list: Optional[List[PeerCompany]] = Field(default_factory=list, alias="peerCompanyList")

class CurrentPrice(BaseModel):
    bse: str = Field(alias="BSE")
    nse: str = Field(alias="NSE")

class StockTechnicalData(BaseModel):
    days: int
    bse_price: str = Field(alias="bsePrice")
    nse_price: str = Field(alias="nsePrice")

class FinancialItem(BaseModel):
    display_name: str = Field(alias="displayName")
    key: str
    value: str
    qo_q_comp: Optional[str] = Field(alias="qoQComp")
    yqo_q_comp: Optional[str] = Field(alias="yqoQComp")

class StockFinancialMap(BaseModel):
    cas: Optional[List[FinancialItem]] = Field(alias="CAS")
    bal: Optional[List[FinancialItem]] = Field(alias="BAL")
    inc: Optional[List[FinancialItem]] = Field(alias="INC")

class StockFinancialData(BaseModel):
    stock_financial_map: StockFinancialMap = Field(alias="stockFinancialMap")
    fiscal_year: str = Field(alias="FiscalYear")
    end_date: str = Field(alias="EndDate")
    type: str = Field(alias="Type")
    statement_date: str = Field(alias="StatementDate")
    fiscal_period_number: int = Field(alias="fiscalPeriodNumber")

class KeyMetricItem(BaseModel):
    display_name: str = Field(alias="displayName")
    key: str
    value: Optional[str]

class KeyMetrics(BaseModel):
    mgmt_effectiveness: List[KeyMetricItem] = Field(alias="mgmtEffectiveness")
    margins: List[KeyMetricItem]
    financial_strength: List[KeyMetricItem] = Field(alias="financialstrength")
    valuation: List[KeyMetricItem]
    income_statement: List[KeyMetricItem] = Field(alias="incomeStatement")
    growth: List[KeyMetricItem]
    per_share_data: List[KeyMetricItem] = Field(alias="persharedata")
    price_and_volume: List[KeyMetricItem] = Field(alias="priceandVolume")

class AnalystRating(BaseModel):
    color_code: str = Field(alias="colorCode")
    rating_name: str = Field(alias="ratingName")
    rating_value: int = Field(alias="ratingValue")
    number_of_analysts_latest: str = Field(alias="numberOfAnalystsLatest")
    number_of_analysts_1week_ago: str = Field(alias="numberOfAnalysts1WeekAgo")
    number_of_analysts_1month_ago: str = Field(alias="numberOfAnalysts1MonthAgo")
    number_of_analysts_2month_ago: str = Field(alias="numberOfAnalysts2MonthAgo")
    number_of_analysts_3month_ago: str = Field(alias="numberOfAnalysts3MonthAgo")

class StockAnalyst(BaseModel):
    color_code: str = Field(alias="colorCode")
    rating_name: str = Field(alias="ratingName")
    rating_value: int = Field(alias="ratingValue")
    min_value: float = Field(alias="minValue")
    max_value: float = Field(alias="maxValue")
    number_of_analysts: int = Field(alias="numberOfAnalysts")

class RecosBar(BaseModel):
    stock_analyst: List[StockAnalyst] = Field(alias="stockAnalyst")
    ticker_rating_value: int = Field(alias="tickerRatingValue")
    is_data_present: bool = Field(alias="isDataPresent")
    no_of_recommendations: int = Field(alias="noOfRecommendations")
    mean_value: float = Field(alias="meanValue")
    ticker_percentage: float = Field(alias="tickerPercentage")

class RiskMeter(BaseModel):
    category_name: str = Field(alias="categoryName")
    std_dev: float = Field(alias="stdDev")

class ShareholdingCategory(BaseModel):
    holding_date: str = Field(alias="holdingDate")
    percentage: str

class Shareholding(BaseModel):
    category_name: str = Field(alias="categoryName")
    display_name: str = Field(alias="displayName")
    categories: List[ShareholdingCategory]

class CorporateActionBase(BaseModel):
    ticker_id: str = Field(alias="tickerId")
    company_name: str = Field(alias="companyName")
    remarks: str

class Dividend(CorporateActionBase):
    record_date: str = Field(alias="recordDate")
    xd_date: str = Field(alias="xdDate")
    interim_or_final: str = Field(alias="interimOrFinal")
    instrument_type: int = Field(alias="instrumentType")
    value: float
    percentage: int
    date_of_announcement: str = Field(alias="dateOfAnnouncement")
    book_closure_start_date: str = Field(alias="bookClosureStartDate")
    book_closure_end_date: str = Field(alias="bookClosureEndDate")
    sort_date: str = Field(alias="sortDate")

class Split(CorporateActionBase):
    record_date: str = Field(alias="recordDate")
    xs_date: str = Field(alias="xsDate")
    old_face_value: int = Field(alias="oldFaceValue")
    new_face_value: int = Field(alias="newFaceValue")
    sort_date: str = Field(alias="sortDate")

class Meeting(CorporateActionBase):
    date_of_announcement: Optional[str] = Field(None, alias="dateOfAnnouncement")
    record_date: Optional[str] = Field(None, alias="recordDate")
    agm_date: Optional[str] = Field(None, alias="agmDate")
    board_meet_date: Optional[str] = Field(None, alias="boardMeetDate")
    purpose: Optional[str] = Field(None)

class StockCorporateActionData(BaseModel):
    bonus: List = []
    dividend: List[Dividend]
    rights: List = []
    splits: List[Split]
    annual_general_meeting: List[Meeting] = Field(alias="annualGeneralMeeting")
    board_meetings: List[Meeting] = Field(alias="boardMeetings")

class StockDetailsReusableData(BaseModel):
    close: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    price: Optional[str] = None
    percent_change: Optional[str] = Field(None, alias="percentChange")
    market_cap: Optional[str] = Field(None, alias="marketCap")
    yhigh: Optional[str] = None
    ylow: Optional[str] = None
    high: Optional[str] = None
    low: Optional[str] = None
    p_per_e_basic_excluding_extraordinary_items_ttm: Optional[str] = Field(None, alias="pPerEBasicExcludingExtraordinaryItemsTTM")
    current_dividend_yield_common_stock_primary_ltm: Optional[str] = Field(None, alias="currentDividendYieldCommonStockPrimaryIssueLTM")
    total_debt_per_total_equity_most_recent_quarter: Optional[str] = Field(None, alias="totalDebtPerTotalEquityMostRecentQuarter")
    price_ytd_price_percent_change: Optional[str] = Field(None, alias="priceYTDPricePercentChange")
    price_5day_percent_change: Optional[str] = Field(None, alias="price5DayPercentChange")
    net_income: Optional[str] = Field(None, alias="NetIncome")
    fiscal_year: Optional[str] = Field(None, alias="FiscalYear")
    interim_net_income: Optional[str] = Field(None, alias="interimNetIncome")
    stock_analyst: Optional[List[AnalystRating]] = Field(default_factory=list, alias="stockAnalyst")
    peer_company_list: Optional[List[PeerCompany]] = Field(default_factory=list, alias="peerCompanyList")
    sector_price_to_earnings_value_ratio: Optional[str] = Field(None, alias="sectorPriceToEarningsValueRatio")
    average_rating: Optional[str] = Field(None, alias="averageRating")
    promoter_share_holding: Optional[str] = Field(None, alias="promoterShareHolding")
    mutual_fund_share_holding: Optional[ShareholdingCategory] = Field(None, alias="mutualFundShareHolding")

class RecentNews(BaseModel):
    id: str
    headline: str
    intro: str
    byline: str
    date: str
    time_to_read: str = Field(alias="timeToRead")
    premium_story: str = Field(alias="premiumStory")
    section: str
    keywords: str
    url: str
    thumbnail_image: str = Field(alias="thumbnailimage")
    list_image: str = Field(alias="listimage")
    small_image: str = Field(alias="smallimage")
    big_image: str = Field(alias="bigimage")
    image_caption: str = Field(alias="imagecaption")
    image_621x414: str = Field(alias="image_621x414")
    image_222x148: str = Field(alias="image_222x148")
    slider_images: List = Field(alias="sliderimages")
    slider_videos: List = Field(alias="slidervideos")
    interactives: List
    body: str


class ISMStockDetailsResponse(BaseModel):
    company_name: str = Field(alias="companyName")
    industry: Optional[str] = None
    company_profile: Optional[CompanyProfile] = Field(None, alias="companyProfile")
    current_price: CurrentPrice = Field(alias="currentPrice")
    stock_technical_data: Optional[List[StockTechnicalData]] = Field(default_factory=list, alias="stockTechnicalData")
    percent_change: Optional[str] = Field(None, alias="percentChange")
    year_high: Optional[str] = Field(None, alias="yearHigh")
    year_low: Optional[str] = Field(None, alias="yearLow")
    financials: Optional[List[StockFinancialData]] = Field(default_factory=list)
    key_metrics: Optional[KeyMetrics] = Field(None, alias="keyMetrics")
    future_expiry_dates: Optional[List] = Field(default_factory=list, alias="futureExpiryDates")
    future_overview_data: Optional[List] = Field(default_factory=list, alias="futureOverviewData")
    initial_stock_financial_data: Optional[List] = Field(default_factory=list, alias="initialStockFinancialData")
    analyst_view: Optional[List[AnalystRating]] = Field(default_factory=list, alias="analystView")
    recos_bar: Optional[RecosBar] = Field(None, alias="recosBar")
    risk_meter: Optional[RiskMeter] = Field(None, alias="riskMeter")
    shareholding: Optional[List[Shareholding]] = Field(default_factory=list)
    stock_corporate_action_data: Optional[StockCorporateActionData] = Field(None, alias="stockCorporateActionData")
    stock_details_reusable_data: StockDetailsReusableData = Field(..., alias="stockDetailsReusableData")
    stock_financial_data: Optional[List[StockFinancialData]] = Field(default_factory=list, alias="stockFinancialData")
    recent_news: Optional[List[RecentNews]] = Field(default_factory=list, alias="recentNews")

    class Config:
        from_attributes = True
        populate_by_name = True