/* Copyright 2024 Camptocamp
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl) */

import {patch} from "@web/core/utils/patch";
import {
    DateTimeField,
    dateRangeField,
    dateTimeField,
} from "@web/views/fields/datetime/datetime_field";
import {
    listDateRangeField,
    listDateTimeField,
} from "@web/views/fields/datetime/list_datetime_field";

/**
 * @typedef {import("./datepicker.esm").DateTimePickerProps} DateTimePickerProps
 */

patch(DateTimeField.prototype, {
    setup() {
        super.setup();

        this.state.defaultTime = this.defaultTime;
        this.state.defaultStartTime = this.defaultStartTime;
        this.state.defaultEndTime = this.defaultEndTime;
    },

    // Getter
    get defaultTime() {
        if (typeof this.props.defaultTime === "string") {
            if (!this.props.record.data[this.props.defaultTime]) {
                return "";
            }
            if (typeof this.props.record.data[this.props.defaultTime] === "string") {
                return JSON.parse(this.props.record.data[this.props.defaultTime]);
            }
            return this.props.record.data[this.props.defaultTime];
        }
        return this.props.defaultTime;
    },

    get defaultStartTime() {
        if (typeof this.props.defaultStartTime === "string") {
            if (!this.props.record.data[this.props.defaultStartTime]) {
                return "";
            }
            if (
                typeof this.props.record.data[this.props.defaultStartTime] === "string"
            ) {
                return JSON.parse(this.props.record.data[this.props.defaultStartTime]);
            }
            return this.props.record.data[this.props.defaultStartTime];
        }
        return this.props.defaultStartTime;
    },

    get defaultEndTime() {
        if (typeof this.props.defaultEndTime === "string") {
            if (!this.props.record.data[this.props.defaultEndTime]) {
                return "";
            }
            if (typeof this.props.record.data[this.props.defaultEndTime] === "string") {
                return JSON.parse(this.props.record.data[this.props.defaultEndTime]);
            }
            return this.props.record.data[this.props.defaultEndTime];
        }
        return this.props.defaultEndTime;
    },

    // OVERRIDE:remove automatic date calculation
    async addDate(valueIndex) {
        this.state.focusedDateIndex = valueIndex;
        this.state.value = this.values;
        this.state.range = true;

        this.openPicker(valueIndex);
    },
});

DateTimeField.props = {
    ...DateTimeField.props,
    defaultTime: {
        type: [
            String,
            {
                type: Object,
                shape: {
                    hour: Number,
                    minute: Number,
                    second: Number,
                },
                optional: true,
            },
        ],
        optional: true,
    },
    defaultStartTime: {
        type: [
            String,
            {
                type: Object,
                shape: {
                    hour: Number,
                    minute: Number,
                    second: Number,
                },
                optional: true,
            },
        ],
        optional: true,
    },
    defaultEndTime: {
        type: [
            String,
            {
                type: Object,
                shape: {
                    hour: Number,
                    minute: Number,
                    second: Number,
                },
                optional: true,
            },
        ],
        optional: true,
    },
};

const superDateTimeExtractProps = dateTimeField.extractProps;
dateTimeField.extractProps = ({attrs, options}, dynamicInfo) => ({
    ...superDateTimeExtractProps({attrs, options}, dynamicInfo),
    defaultTime: options.defaultTime,
});

const superDateRangeExtractProps = dateRangeField.extractProps;
dateRangeField.extractProps = ({attrs, options}, dynamicInfo) => ({
    ...superDateRangeExtractProps({attrs, options}, dynamicInfo),
    defaultStartTime: options.defaultStartTime,
    defaultEndTime: options.defaultEndTime,
});

const superListDateTimeExtractProps = listDateTimeField.extractProps;
listDateTimeField.extractProps = ({attrs, options}, dynamicInfo) => ({
    ...superListDateTimeExtractProps({attrs, options}, dynamicInfo),
    defaultTime: options.defaultTime,
});

const superListDateRangeExtractProps = listDateRangeField.extractProps;
listDateRangeField.extractProps = ({attrs, options}, dynamicInfo) => ({
    ...superListDateRangeExtractProps({attrs, options}, dynamicInfo),
    defaultStartTime: options.defaultStartTime,
    defaultEndTime: options.defaultEndTime,
});
