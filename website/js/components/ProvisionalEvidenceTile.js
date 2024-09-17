'use strict';
import util from '../util';
import React from 'react';
import {Table} from "react-bootstrap";
import * as _ from 'lodash';
import classNames from "classnames";
var KeyInline = require('./KeyInline');
const slugify = require('../slugify');
import CollapsibleTile from "./collapsible/CollapsibleTile";
import CollapsibleSection from "./collapsible/CollapsibleSection";

// ACMG Variant Evidence Codes, Provisional Assignment
export default class ProvisionalEvidenceTile extends React.Component {

    // For the sub-tile headers that have a result value displayed in the header,
    // Add css so that the value floats to the right
    generateHeader(result) {
        return (
            <div className="func-assay-extras">
                <span className="func-assay-result" style={{float: 'right', paddingRight: '10px'}}>{result}</span>
                <div style={{clear: 'both'}}></div>
            </div>
        );
    }

    // Given a group source (ie groupname), data (list of dicts containing title:, prop:), and variant object
    // generate table rows to be displayed in that group's section
    // retrieving the requested prop values from the variant
    // and applying the corresponding help tooltips
    getRowsAndDetermineIfEmpty(source, data, variant, emptyTracker) {
        const rows = _.map(data, (rowDescriptor) => {
            //let {prop, title, noHelpLink} = rowDescriptor;
            let {prop, title} = rowDescriptor;

            const rowItem = util.getFormattedFieldByProp(prop, variant);
            const isEmptyValue = util.isEmptyField(rowItem);
            if (!isEmptyValue) { // We found a nonempty value - update trackEmptyRows
                emptyTracker.allEmpty = false ;
            }
            let rowClasses = classNames({
                'variantfield-empty': (isEmptyValue && this.props.hideEmptyItems),
            });
            return (
                <tr key={prop} className={rowClasses}>
                    <KeyInline tableKey={title} noHelpLink={false}
                        tooltip={this.props.tooltips && this.props.tooltips[slugify(prop)]}
                        onClick={(event) => this.props.showHelp(event, prop)}
                    />
                    <td><span className={"row-value" }>{rowItem}</span></td>
                </tr>
            );
        });
        return rows;
    }

    render() {
        const {variant, innerGroups} = this.props;
        // start with the assumption all rows are empty and set to false if we find a non-empty row
        // use an object instead of plain bool so we can set it directly when passed into getRowsAndDetermineIfEmpty
        let trackEmptyRows = { allEmpty: true };

        // innerGroup are: Population Frequency, Computational Prediction
        let sections = _.map(innerGroups, (group) => {
            let groupSource = group.source;
            let groupData = group.data;
            let renderedRows = this.getRowsAndDetermineIfEmpty(groupSource, groupData, variant, trackEmptyRows);

            // TEMPORARY - hide ComputationalPrediction subsection until data is populated
            if (groupSource === "Computational Prediction") {
                return ( <div id={groupSource}/> );
            }

            // Attempt to retrieve the prop name of the provisional code so we can put the value in the subsection header
            let extraHeaderProp = false ;
            for ( const dataItem of groupData ) {
                if (dataItem.title === "Provisionally Assigned" ) {
                    extraHeaderProp = dataItem.prop ;
                }
            }
            // If we found a prop, pull it from the variant. If not, leave as a dash.
            let extraHeaderValue = extraHeaderProp ? util.getFormattedFieldByProp(extraHeaderProp, variant) : "-";

            return ( <CollapsibleSection
                    fieldName={groupSource}
                    id={groupSource} // id needed so that when you collapse one the others don't also collapse
                    extraHeaderItems={this.generateHeader(extraHeaderValue)}
                    twoColumnExtraHeader={true}
                    >
                        <Table>
                            <tbody>
                                { renderedRows }
                            </tbody>
                        </Table>
                    </CollapsibleSection>);
        });

        return (
            <CollapsibleTile allEmpty={trackEmptyRows.allEmpty} {...this.props}>
                <div className="tile-disclaimer">
                    The ClinGen <a href="https://cspec.genome.network/cspec/ui/svi/affiliation/50087">
                        ENIGMA Variant Curation Expert Panel (VCEP) rules (Version 1.1.0, dated 2023-11-22)
                    </a> define how the evidence on a variant can contribute to the variant being curated as
                    Pathogenic or Benign, following the <a href="https://pubmed.ncbi.nlm.nih.gov/25741868/">
                        ACMG/AMP standards and guidelines
                    </a>. We have evaluated the following categories of evidence
                    for each variant against the VCEP rules, to evaluate which evidence codes the variant meets.
                    <b> These are provisional evidence code assignments. In general, they have not yet been reviewed by the
                    VCEP biocuration team.</b>  If the variant has been curated by the VCEP, then the
                    Variant Curation Expert Panel tile will contain information on the evidence used for curation.
                </div>
                {sections}
            </CollapsibleTile>
        );
    }
};

